from abc import ABC, abstractmethod
from src.mappers.base_mapper import BaseMapper


class FieldStrategy(ABC):

    @abstractmethod
    def create(self, issue: dict) -> dict | None:
        pass

    @abstractmethod
    def update(self, current_issue: dict, new_issue: dict) -> dict | None:
        pass



class SummaryStrategy(FieldStrategy):
    def create(self, issue: dict) -> dict | None:
        return {"summary": issue.get("title", "No title")}

    def update(self, current_issue: dict, new_issue: dict) -> dict | None:
        if current_issue.get("summary") != new_issue.get("title"):
            return {"summary": new_issue.get("title")}
        return None


class DescriptionStrategy(FieldStrategy):
    def create(self, issue: dict) -> dict | None:
        return {"description": BaseMapper.format_description(issue)}

    def update(self, current_issue: dict, new_issue: dict) -> dict | None:
        new_desc = BaseMapper.format_description(new_issue)
        if current_issue.get("description") != new_desc:
            return {"description": new_desc}
        return None


class StateStrategy(FieldStrategy):
    state_map = {"open": "To do", "closed": "Done"}

    def create(self, issue: dict) -> dict | None:
        new_state = self.state_map.get(issue.get("state"))
        if new_state:
            return {
                "customFields": [{
                    "name": "State",
                    "$type": "StateIssueCustomField",
                    "value": {"name": new_state}
                }]
            }
        return None

    def update(self, current_issue: dict, new_issue: dict) -> dict | None:
        new_state = self.state_map.get(new_issue.get("state"))
        current_state = next(
            (cf.get("value", {}).get("name")
             for cf in current_issue.get("customFields", [])
             if cf.get("name") == "State"),
            None
        )

        if new_state and new_state != current_state:
            return {
                "customFields": [{
                    "name": "State",
                    "$type": "StateIssueCustomField",
                    "value": {"name": new_state}
                }]
            }
        return None


class AssigneeStrategy(FieldStrategy):
    def create(self, issue: dict) -> dict | None:
        assignee_login = issue.get("assignee_login")
        if not assignee_login:
            return None

        return {
            "customFields": [
                {
                    "name": "Assignee",
                    "$type": "SingleUserIssueCustomField",
                    "value": {"login": assignee_login}
                }
            ]
        }

    def _get_assignee_login(self, issue, source: str):
        """
        Gets the field from the json format
        works in 2 modes:
        from github and
        from youtrack format
        """
        if source == "github":
            assignee = issue.get("assignee")
            return assignee.get("login") if assignee else None

        elif source == "youtrack":
            for field in issue.get('customFields', []):
                if field.get('name') == 'Assignee' and field.get('value'):
                    return field['value'].get('login')
            return None

        return None

    def update(self, current_issue: dict, new_issue: dict) -> dict | None:

        current_assignee = self._get_assignee_login(current_issue, source="youtrack")
        new_assignee = self._get_assignee_login(new_issue, source="github")

        if new_assignee and new_assignee != current_assignee:
            return {
                "customFields": [
                    {
                        "name": "Assignee",
                        "$type": "SingleUserIssueCustomField",
                        "value": {"login": new_assignee}
                    }
                ]
            }

        if current_assignee and not new_assignee:
            return {
                "customFields": [
                    {
                        "name": "Assignee",
                        "$type": "SingleUserIssueCustomField",
                        "value": None
                    }
                ]
            }

        return None


