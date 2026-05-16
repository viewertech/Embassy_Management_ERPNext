import frappe
from embassy_management.setup import ensure_roles


def execute():
    ensure_roles()
