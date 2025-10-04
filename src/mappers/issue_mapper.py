import pprint

from src.mappers.base_mapper import BaseMapper

class IssueMapper(BaseMapper):
    def __init__(self, strategies):
        self.strategies = strategies

    def map_create(self, issue: dict, project_id: str) -> dict:
        payload = {"project": {"id": project_id}}
        for strat in self.strategies:
            part = strat.create(issue)
            if part:
                if "customFields" in part:
                    payload.setdefault("customFields", []).extend(part["customFields"])
                else:
                    payload.update(part)
        return payload

    def map_update(self, current_issue: dict, new_issue: dict) -> dict:
        # print(f"CURR-->")
        # pprint.pprint(current_issue)
        # print(f"New-->")
        # pprint.pprint(new_issue)
        payload = {}
        custom_fields = []
        # print(custom_fields)
        for strat in self.strategies:
            part = strat.update(current_issue, new_issue)
            if part:
                if "customFields" in part:
                    custom_fields.extend(part["customFields"])
                else:
                    payload.update(part)
        if custom_fields:
            payload["customFields"] = custom_fields
        return payload
