# Deploy in 3 Steps

## 1. Generate Flow
```bash
cd full_example
python flow_generator.py
```

## 2. Deploy to AWS
```bash
cd terraform
terraform init
terraform apply  # Type 'yes' when prompted
```

## 3. Test
1. Open the dashboard URL from terraform output
2. Claim a phone number
3. Assign "Counter Flow" to it
4. Call the number!

Each caller hears: "Thank you for calling... You are caller number X"

---

**Cost:** ~$4/month for 1000 calls  
**Cleanup:** `terraform destroy`
