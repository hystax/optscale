"""Shared helpers for native Azure recommendation modules.

Modules in this package isolate Azure SDK / Retail Prices interactions so
recommendation modules under bumiworker.bumiworker.modules.recommendations.*
import from a single location and never duplicate pricing/metric logic.

All Azure SDK calls use `azure.identity.ClientSecretCredential` (the
TokenCredential protocol). SDK pins resolve transitively from
`tools/cloud_adapter`; net-new pins live in
`bumiworker/requirements-azure.txt`.
"""
