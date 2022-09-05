from sys import stderr

from requests import HTTPError

from artifactory_cleanup.rules.base import Rule
from artifactory_cleanup.rules.exception import PolicyException


class Repo(Rule):
    """
    Apply the rule to one repository.
    If no name is specified, it is taken from the rule name::

        CleanupPolicy(
           'myrepo.snapshot',
           # if the rule is one for all repositories - you can skip duplicate name
           rules.repo,
           ...
        ),

    """

    def __init__(self, name: str):
        bad_sym = set("*/[]")
        if set(name) & bad_sym:
            raise PolicyException(
                "Bad name for repo: {name}, contains bad symbols: {bad_sym}\n"
                "Check that your have repo() correct".format(
                    name=name, bad_sym="".join(bad_sym)
                )
            )
        self.repo = name

    def aql_add_items_find_filters(self, aql_query_list):
        print("Get from {}".format(self.repo))
        try:
            print("Checking the existence of the {} repository".format(self.repo))
            url = f"/api/storage/{self.repo}"
            r = self.session.get(url)
            r.raise_for_status()
            print("The {} repository exists".format(self.repo))
        except HTTPError as e:
            stderr.write("The {} repository does not exist".format(self.repo))
            print(e)
            exit(1)

        update_dict = {
            "repo": {
                "$eq": self.repo,
            }
        }
        aql_query_list.append(update_dict)
        return aql_query_list


class RepoByMask(Rule):
    """
    Apply rule to repositories matching by mask
    """

    def __init__(self, mask):
        self.mask = mask

    def aql_add_items_find_filters(self, aql_query_list):
        print("Get from {}".format(self.mask))
        update_dict = {
            "repo": {
                "$match": self.mask,
            }
        }
        aql_query_list.append(update_dict)
        return aql_query_list


class PropertyEq(Rule):
    """Deletes repository artifacts with a specific property value only"""

    def __init__(self, property_key, property_value):
        self.property_key = property_key
        self.property_value = property_value

    def aql_add_items_find_filters(self, aql_query_list):
        update_dict = {
            "$and": [
                {"property.key": {"$eq": self.property_key}},
                {"property.value": {"$eq": self.property_value}},
            ]
        }
        aql_query_list.append(update_dict)
        return aql_query_list


class PropertyNeq(Rule):
    """
    Delete repository artifacts only if the value is not equal to the specified one.
    If there is no value, delete it anyway.

    You can specify a flag to not delete ``do_not_delete=1``::

        PropertyNeq('do_not_delete", '1')
    """

    def __init__(self, property_key, property_value):
        self.property_key = property_key
        self.property_value = str(property_value)

    def filter(self, artifacts):
        good_artifact = [
            x
            for x in artifacts
            if x["properties"].get(self.property_key) == self.property_value
        ]
        self.remove_artifact(good_artifact, artifacts)
        return artifacts


# under_score - old style of naming
# Keep it for backward compatibility
repo = Repo
repo_by_mask = RepoByMask
property_eq = PropertyEq
property_neq = PropertyNeq
