from dashing.widgets import ListWidget
from dashing.widgets import NumberWidget
from dashing.widgets import Widget

class WidgetPartyWidget(Widget):
    title = ""

    def get_context(self):
        return {
            'title': self.get_title(),
            'data': self.get_data(),
        }

    def get_title(self):
        return self.title
    
    def get_data(self):
        pass

class IssuesClosed(WidgetPartyWidget):
    title = "Issues Closed"

    def get_data(self):
        return [
            {
                'url': 'https://github.com/SalesforceFoundation/Cumulus/issues/1864',
                'message': '#1864',
            },
            {
                'url': 'https://github.com/SalesforceFoundation/Cumulus/issues/2636',
                'message': '#2636',
            },
            {
                'url': 'https://github.com/SalesforceFoundation/Cumulus/issues/2713',
                'message': '#2713',
            },

        ]

class LatestBeta(WidgetPartyWidget):
    title = "Latest Beta Release"

    def get_context(self):
        context = super(LatestBeta, self).get_context()
    
    def get_data(self):
        return [
            {
                'url': '/api/repository/SalesforceFoundation/Cumulus/3.109'
                'message': '3.109',
            }
        ]

class ReleasesBeta(Widget):
    title = 'Latest Beta Release'

    def get_data(self):
        return '3.110 (Beta 6)'

class ReleaseDates(ListWidget):
    title = 'Release Dates'

    def get_data(self):
        return [
            {
                'label': 'Release Created',
                'value': 'Oct 11, 2017',
            },
            {
                'label': 'Push to Sandbox',
                'value': 'Oct 11, 2017',
            },
            {
                'label': 'Push to Production',
                'value': 'Oct 17, 2017',
            },
        ]

    def get_more_info(self):
        return "These are the scheduled push dates when this version will be pushed to production and sandbox orgs"

class ReleaseNotesSummary(ListWidget):
    title = "Release Notes Summary"

    def get_data(self):
        return [
            {
                'label': 'Critical Changes',
                'value': '0',
            },
            {
                'label': 'Changes',
                'value': '4',
            },
            {
                'label': 'Issues Closed',
                'value': '4',
            },
            {
                'label': 'New Metadata',
                'value': '9',
            },
            {
                'label': 'Deleted Metadata',
                'value': '2',
            },
        ]

