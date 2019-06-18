import errno
import signal
import os

from django.db import DatabaseError, InterfaceError, connections
from rq.worker import StopRequested
from rq.worker import signal_name
from rq.worker import Worker


class RequeueingWorker(Worker):
    """
    An extension of the base rq worker which handles requeueing the job if
    SIGTERM or SIGINT causes the worker to close. This currently uses the delay
    method on the target function so the function must support that.

    Also ensures db connection is closed before and after each job.
    """

    def _install_signal_handlers(self):
        """
        Installs signal handlers for handling SIGINT and SIGTERM gracefully.
        """
        signal.signal(signal.SIGINT, self.request_stop)
        signal.signal(signal.SIGTERM, self.request_stop)

    def request_force_stop(self, signum, frame):
        """
        Terminates the application (cold shutdown).
        """
        self.log.warning("Cold shut down.")

        # If shutdown is requested in the middle of a job, requeue the job
        if self.get_current_job():
            job = self.get_current_job()
            job.func.delay(*job.args, **job.kwargs)

        # Take down the horse with the worker
        if self.horse_pid:
            self.log.debug("Taking down horse %d with me." % self.horse_pid)
            try:
                os.kill(self.horse_pid, signal.SIGKILL)
            except OSError as e:
                # ESRCH ("No such process") is fine with us
                if e.errno != errno.ESRCH:
                    self.log.debug("Horse already down.")
                    raise

        raise SystemExit()

    def request_stop(self, signum, frame):
        """
        Stops the current worker loop but waits for child processes to end
        gracefully (warm shutdown).
        """
        self.log.info("Got signal %s." % signal_name(signum))

        signal.signal(signal.SIGINT, self.request_force_stop)
        signal.signal(signal.SIGTERM, self.request_force_stop)

        self.log.warning("Warm shut down requested.")

        # If shutdown is requested in the middle of a job, wait until
        # finish before shutting down
        if self.get_current_job():
            self._stopped = True
            self.log.info(
                "Stopping after current horse is finished. "
                "Press Ctrl+C again for a cold shutdown."
            )
        else:
            raise StopRequested()

    def close_database(self):
        for connection in connections.all():
            try:
                connection.close()
            except InterfaceError:
                pass
            except DatabaseError as e:
                str_exc = str(e)
                if "closed" not in str_exc and "not connected" not in str_exc:
                    raise

    def perform_job(self, *args, **kwargs):
        self.close_database()
        try:
            return super().perform_job(*args, **kwargs)
        finally:
            self.close_database()
