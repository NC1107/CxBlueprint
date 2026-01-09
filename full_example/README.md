# Simple Counter Example

Minimal Amazon Connect + Lambda example showing how to use CxBlueprint.

## What It Does

1. Caller hears: "Thank you for calling"
2. Lambda increments counter stored in /tmp
3. Caller hears: "You are caller number X"
4. Call disconnects

## Architecture

```
CxBlueprint -> counter_flow.json -> Terraform deploys:
                                   - Connect Instance
                                   - Contact Flow
                                   - Lambda
```

## Quick Start

```bash
# 1. Generate flow
python flow_generator.py

# 2. Deploy
cd terraform
terraform init
terraform apply

# 3. Request phone number quota increase via AWS Console
# (New instances default to 0 phone numbers)

# 4. Claim number and test
```

## Files

- `flow_generator.py` - Uses CxBlueprint as library
- `counter_flow.json` - Generated flow (4 blocks)
- `lambda/counter.py` - /tmp-backed counter (40 lines)
- `terraform/` - Infrastructure code (110 lines)

## Monitoring

```bash
# View logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

## Cost

**~$3/month** for 1000 calls

- Connect: $3.60
- Lambda: $0.20

## Cleanup

```bash
cd terraform
terraform destroy
```
