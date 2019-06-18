from unittest.mock import MagicMock
import signal

import pytest
from django.db import DatabaseError, InterfaceError
from django_rq import get_worker
from rq.worker import StopRequested


class TestRequeueingWorker:
    def test_install_signal_handlers(self, mocker):
        signal = mocker.patch("signal.signal")
        worker = get_worker()
        worker._install_signal_handlers()
        assert signal.call_count == 2

    def test_request_stop(self, mocker):
        signal = mocker.patch("signal.signal")
        worker = get_worker()
        with pytest.raises(StopRequested):
            worker.request_stop(signal.SIGINT, None)

        # new signal handlers installed
        assert signal.call_count == 2

    def test_request_stop__current_job(self, mocker):
        signal = mocker.patch("signal.signal")
        worker = get_worker()
        worker.get_current_job = mocker.MagicMock()
        worker.request_stop(signal.SIGINT, None)

        # worker flagged to stop
        assert worker._stopped

    def test_request_force_stop(self, mocker):
        kill = mocker.patch("os.kill")
        worker = get_worker()
        job = mocker.MagicMock()
        worker.get_current_job = mocker.MagicMock(return_value=job)
        worker._horse_pid = 1
        with pytest.raises(SystemExit):
            worker.request_force_stop(signal.SIGTERM, None)

        job.func.delay.assert_called_once()
        kill.assert_called_once_with(1, signal.SIGKILL)

    def test_request_force_stop__dead_horse(self, mocker):
        kill = mocker.patch("os.kill", side_effect=OSError)
        worker = get_worker()
        job = mocker.MagicMock()
        worker._horse_pid = 1
        with pytest.raises(OSError):
            worker.request_force_stop(signal.SIGTERM, None)

    def test_close_database__good(self, mocker):
        conn = MagicMock()
        all_ = mocker.patch("django.db.connections.all")
        all_.return_value = [conn]

        worker = get_worker()
        worker.close_database()

        assert conn.close.called

    def test_close_database__interface_error(self, mocker):
        conn = MagicMock()
        conn.close.side_effect = InterfaceError()
        all_ = mocker.patch("django.db.connections.all")
        all_.return_value = [conn]

        worker = get_worker()
        worker.close_database()

        assert conn.close.called

    def test_close_database__database_error__reraise(self, mocker):
        conn = MagicMock()
        conn.close.side_effect = DatabaseError("reraise me")
        all_ = mocker.patch("django.db.connections.all")
        all_.return_value = [conn]

        worker = get_worker()
        with pytest.raises(DatabaseError):
            worker.close_database()

    def test_close_database__database_error__no_reraise(self, mocker):
        conn = MagicMock()
        conn.close.side_effect = DatabaseError("closed not connected don't reraise me")
        all_ = mocker.patch("django.db.connections.all")
        all_.return_value = [conn]

        worker = get_worker()
        worker.close_database()

        assert conn.close.called

    def test_perform_job(self, mocker):
        close_database = mocker.patch(
            "statusite.worker.RequeueingWorker.close_database"
        )
        mocker.patch("rq.worker.Worker.perform_job")

        worker = get_worker()
        # Symbolic call only, since we've mocked out the super:
        worker.perform_job(None, None)

        assert close_database.called
