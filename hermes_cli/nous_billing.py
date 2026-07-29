"""Disabled Nous billing client for the lite build."""


class BillingError(RuntimeError):
    pass


class BillingScopeRequired(BillingError):
    pass


def _disabled(*args, **kwargs):
    raise BillingError("Nous billing is disabled in the lite build.")


post_subscription_preview = _disabled
post_charge = _disabled
get_billing_status = _disabled
get_meter_summary = _disabled
get_recent_charges = _disabled
get_subscription_preview = _disabled
get_subscription_status = _disabled
