# Sync BE RUN

This README provides instructions for setting up and running the synchronization backend system.

## Prerequisites

- Python 3.x
- Redis
- FastAPI
- RQ (Redis Queue)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Terminal 1 (Run FastAPI App)

```bash
uvicorn app:app --reload
```

## Terminal 2 (Run Redis Server)

```bash
sudo redis-stack-server
```

## Terminal 3 (Redis Configuration)

```bash
 redis-cli
 ```

```bash
 FT.CREATE co_sync_fields_mapping ON JSON PREFIX 1 conf:co_sync:fields:mapping: SCHEMA $.chargeover_field as chargeover_field TEXT SORTABLE $.object as object TEXT $.production as production TAG $.staging as staging TAG
 ```

## Terminal 4 (Python Test Script)
### Create File

``` 
test.py
```

```
from atp.salesforce.common.models import OrgParamsModel
from models.config import ChargeOverApiConf

try:
    OrgParamsModel(
        pk="production",
        client_id="3MVG9rFJvQRVOvk67vZhP71kQut14mdhMg3Cg_hv5WI.XhNvs.xGeUP.i_JHeEfZA2Fy198qq1MpxKka8u_H3",
        client_secret="9262304F42B62FBCEB9880C06BB4FEA148562CDC3E2D8C1B52723D3C63A5D2DC",
        org_url="https://college-prep.my.salesforce.com",
        org_id="00Dd0000000d5fDEAQ",
        api_version="v58.0",
        access_token=None,
        co_sync=True,
        co_env="production",
    ).save()
    OrgParamsModel(
        pk="staging",
        client_id="3MVG9dzDZFnwTBRL2_PjD.38G2wGSRO6kvs4Xs0aXANzHNYWeNxFiSlyw0qFb5OhygaH8tMzNazYGY7RddX0D",
        client_secret="161943B16ADC31A4C9A915576A032565D8C8B41438E5271074042F049DA267C8",
        org_url="https://college-prep--staging.sandbox.my.salesforce.com",
        org_id="00D6t0000004fD9EAI",
        api_version="v58.0",
        access_token=None,
        co_sync=True,
        co_env="staging",
    ).save()
    
except Exception as e:
    print(e)
    
retrieved_instance = OrgParamsModel.get("staging")

print(retrieved_instance)

ChargeOverApiConf(
    pk="production",
    endpoint='https://chargeover.com/api/v3',
    username='zDj2qINTS0tgKh8AEdRa6BnlfZFGVk4b',
    password='TIf3jR1PXULNHcZz5gsdCpuk0atOrQGh'
).save()

ChargeOverApiConf(
    pk="staging",
    endpoint='https://achieve-staging.chargeover.com/api/v3',
    username='fw69l4EGHByuKc30q8MOR7PdemVIJnr1',
    password='gmUuIWVYQhHTXSpfEyRia36G0wc597C4'
).save()

```
### Execute the script:

```bash
python test.py
```

## Terminal 5 (Run RQ Worker)

```bash
rq worker staging -c handlers.background.settings --with-scheduler
```

## Terminal 6 (Seed Redis Configuration)

```bash
python seed_redis_config.py
```

