"""Disabled billing mixin for the lite build."""


class CLIBillingMixin:
    def _show_subscription(self, *args, **kwargs):
        self._vprint("Subscriptions are disabled in the lite build.", force=True)

    def _show_billing(self, *args, **kwargs):
        self._vprint("Billing and top-up are disabled in the lite build.", force=True)
