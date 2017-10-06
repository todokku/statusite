from dashing.utils import router
from statusite.dashboard.widgets import IssuesClosed
from statusite.dashboard.widgets import ReleaseDates
from statusite.dashboard.widgets import ReleaseNotesSummary

router.register(IssuesClosed, 'issues_closed_widget')
router.register(ReleaseDates, 'release_dates_widget')
router.register(ReleaseNotesSummary, 'release_notes_summary_widget')
