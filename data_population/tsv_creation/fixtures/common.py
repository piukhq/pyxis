audit_data = [
    {
        "request": {
            "url": "http://polaris-api/bpl/loyalty/test-retailer/accounts/67f25342-158b-44e0-b5c3-24cedf49b750/adjustments"
        },
        "response": {"body": "{new_balance:375, campaign_slug:test-campaign-1}", "status": 200},
        "timestamp": "2021-11-01T15:39:40.050413",
    },
    {
        "request": {"url": "http://carina-api/bpl/vouchers/test-retailer/vouchers/10percentoff/allocation"},
        "response": {"body": "{}", "status": 202},
        "timestamp": "2021-11-01T15:39:40.138773",
    },
]