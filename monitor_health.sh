#!/bin/bash

INSTANCE_ID="i-05ee547f4d794a8f2"  # Your EC2 instance ID
REGION="ap-south-1"              # Your AWS region
SNS_TOPIC_ARN="arn:aws:sns:ap-south-1:193926907804:Standard"

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$BACKEND_STATUS" -ne 200 ]; then
    aws sns publish \
        --region $REGION \
        --topic-arn $SNS_TOPIC_ARN \
        --subject "🚨 Backend Health Check Failed" \
        --message "Backend returned status code: $BACKEND_STATUS at $(date)"
fi

# Check frontend health
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://tigerosint.aptsoftware.in)

if [ "$FRONTEND_STATUS" -ne 200 ]; then
    aws sns publish \
        --region $REGION \
        --topic-arn $SNS_TOPIC_ARN \
        --subject "🚨 Frontend Health Check Failed" \
        --message "Frontend returned status code: $FRONTEND_STATUS at $(date)"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 85 ]; then
    aws sns publish \
        --region $REGION \
        --topic-arn $SNS_TOPIC_ARN \
        --subject "⚠️ High Disk Usage Alert" \
        --message "Disk usage is at ${DISK_USAGE}% on $(date)"
fi

# Check if Docker containers are running
BACKEND_RUNNING=$(docker ps --filter "name=socialSearcher_backend" --format "{{.Status}}" | grep -c "Up")
FRONTEND_RUNNING=$(docker ps --filter "name=socialSearcher_frontend" --format "{{.Status}}" | grep -c "Up")

if [ "$BACKEND_RUNNING" -eq 0 ] || [ "$FRONTEND_RUNNING" -eq 0 ]; then
    aws sns publish \
        --region $REGION \
        --topic-arn $SNS_TOPIC_ARN \
        --subject "🚨 Container Down Alert" \
        --message "Backend running: $BACKEND_RUNNING, Frontend running: $FRONTEND_RUNNING at $(date)"
fi