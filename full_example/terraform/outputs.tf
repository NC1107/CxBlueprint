output "connect_instance_id" {
  description = "Amazon Connect Instance ID"
  value       = aws_connect_instance.counter_demo.id
}

output "connect_instance_alias" {
  description = "Amazon Connect Instance Alias"
  value       = aws_connect_instance.counter_demo.instance_alias
}

output "lambda_function_name" {
  description = "Counter Lambda Function Name"
  value       = aws_lambda_function.counter.function_name
}

output "contact_flow_id" {
  description = "Contact Flow ID"
  value       = aws_connect_contact_flow.counter_flow.contact_flow_id
}

output "dashboard_url" {
  description = "Connect Dashboard URL"
  value       = "https://${aws_connect_instance.counter_demo.instance_alias}.my.connect.aws/"
}

output "test_instructions" {
  description = "How to test"
  value       = <<-EOT
    Deployed Successfully!
    
    Next steps:
    1. Open: https://${aws_connect_instance.counter_demo.instance_alias}.my.connect.aws/
    2. Claim a phone number
    3. Assign "Counter Flow" to the number
    4. Call the number
    
    View logs:
      aws logs tail /aws/lambda/${aws_lambda_function.counter.function_name} --follow
  EOT
}
