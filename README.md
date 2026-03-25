# PDF Extract Service SQS 📄☁️

**AWS SQS-Triggered PDF Extraction and Processing Microservice**

A production-ready microservice that processes PDFs triggered by AWS SQS messages, extracts content, and stores results with containerized deployment on AWS Lambda.

---

## 🌟 Features

- 📄 **PDF Processing** - Extract text and data from PDFs
- 📨 **SQS Integration** - Event-driven processing
- ☁️ **AWS Lambda** - Serverless deployment
- 🐳 **Containerized** - Docker support
- 💾 **S3 Integration** - Store results in S3
- 🔄 **Queue Management** - Handle large volumes
- 📊 **Metadata Extraction** - Extract document info
- 🔐 **Error Handling** - Robust error management

---

## 🛠️ Tech Stack

**Core:**
- Python 3.10+
- PyPDF (PDF processing)
- Boto3 (AWS SDK)

**AWS Services:**
- SQS (Simple Queue Service)
- Lambda (Serverless compute)
- S3 (Object storage)
- CloudWatch (Logging)

**Infrastructure:**
- Docker
- AWS Lambda

---

## 📊 Language Composition

```
Python: 92.5%
Dockerfile: 7.5%
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- AWS Account with permissions
- Docker (for local testing)
- AWS CLI configured

### Installation

```bash
# Clone the repository
git clone https://github.com/saumaykilla/pdf-extract-service-sqs.git
cd pdf-extract-service-sqs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create `.env`:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
SQS_QUEUE_URL=https://sqs.{region}.amazonaws.com/{account}/queue-name
S3_BUCKET=your-bucket-name
```

---

## 📁 Project Structure

```
pdf-extract-service-sqs/
├── src/
│   ├── __init__.py
│   ├── handler.py          # Lambda handler
│   ├── pdf_extractor.py    # PDF processing
│   ├── sqs_processor.py    # SQS handling
│   ├── s3_uploader.py      # S3 integration
│   ├── models.py           # Data models
│   ├── config.py           # Configuration
│   └── utils.py            # Utilities
├── tests/
│   ├── test_handler.py
│   ├── test_extractor.py
│   └── test_sqs.py
├── Dockerfile
├── requirements.txt
├── lambda_function.py      # Entry point
└── README.md
```

---

## 🔧 Core Components

### PDF Extractor

```python
from src.pdf_extractor import PDFExtractor

extractor = PDFExtractor()

# Extract text
text = extractor.extract_text("document.pdf")

# Extract metadata
metadata = extractor.extract_metadata("document.pdf")

# Extract all
data = extractor.extract_all("document.pdf")
```

### SQS Processor

```python
from src.sqs_processor import SQSProcessor

processor = SQSProcessor(queue_url)

# Get messages
messages = processor.get_messages(max_count=10)

# Process message
for message in messages:
    try:
        processor.process_message(message)
        processor.delete_message(message)
    except Exception as e:
        processor.send_to_dlq(message, error=str(e))
```

### S3 Uploader

```python
from src.s3_uploader import S3Uploader

uploader = S3Uploader(bucket_name)

# Upload file
uploader.upload_file("local.txt", "s3/path/file.txt")

# Upload data
uploader.upload_data(data, "s3/path/data.json")
```

### Lambda Handler

```python
# lambda_function.py
from src.handler import lambda_handler

def handler(event, context):
    return lambda_handler(event, context)
```

---

## 💻 Usage Examples

### Local Testing

```python
from src.pdf_extractor import PDFExtractor
from src.sqs_processor import SQSProcessor
from src.s3_uploader import S3Uploader

# Initialize components
extractor = PDFExtractor()
s3 = S3Uploader("my-bucket")

# Process PDF
pdf_path = "sample.pdf"
text = extractor.extract_text(pdf_path)
metadata = extractor.extract_metadata(pdf_path)

# Upload to S3
result = {
    'text': text,
    'metadata': metadata
}
s3.upload_data(result, f"results/{pdf_path}.json")
```

### SQS Processing Loop

```python
import time
from src.sqs_processor import SQSProcessor
from src.pdf_extractor import PDFExtractor

processor = SQSProcessor(queue_url)
extractor = PDFExtractor()

while True:
    messages = processor.get_messages()
    
    for message in messages:
        try:
            # Extract PDF key from message
            pdf_key = message['Body']['pdf_s3_key']
            
            # Process
            result = extractor.extract_all(pdf_key)
            
            # Upload result
            s3.upload_data(result, f"output/{pdf_key}.json")
            
            # Delete from queue
            processor.delete_message(message)
            
        except Exception as e:
            print(f"Error: {e}")
            processor.send_to_dlq(message, str(e))
    
    time.sleep(1)
```

### Batch Processing

```python
import json
from src.pdf_extractor import PDFExtractor
from src.s3_uploader import S3Uploader

extractor = PDFExtractor()
s3 = S3Uploader("bucket")

# List all PDFs in S3
s3_keys = s3.list_objects("pdfs/")

results = []
for key in s3_keys:
    try:
        data = extractor.extract_all(key)
        results.append({
            'key': key,
            'status': 'success',
            'data': data
        })
    except Exception as e:
        results.append({
            'key': key,
            'status': 'error',
            'error': str(e)
        })

# Save results
s3.upload_data(results, "batch-results.json")
```

---

## 🏗️ AWS Lambda Deployment

### Create Lambda Function

```bash
# Package code
zip -r function.zip src/ lambda_function.py requirements.txt

# Create function
aws lambda create-function \
  --function-name pdf-extractor \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_function.handler \
  --zip-file fileb://function.zip

# Update environment
aws lambda update-function-configuration \
  --function-name pdf-extractor \
  --environment Variables={SQS_QUEUE_URL=queue-url,S3_BUCKET=bucket}
```

### Setup SQS Trigger

```bash
# Create event source mapping
aws lambda create-event-source-mapping \
  --event-source-arn arn:aws:sqs:region:account:queue \
  --function-name pdf-extractor \
  --batch-size 10
```

---

## 🐳 Docker Build & Deployment

### Dockerfile

```dockerfile
FROM public.ecr.aws/lambda/python:3.10

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY src/ ${LAMBDA_TASK_ROOT}/src/
COPY lambda_function.py ${LAMBDA_TASK_ROOT}/

CMD [ "lambda_function.handler" ]
```

### Build and Push

```bash
# Build image
docker build -t pdf-extractor:latest .

# Tag for ECR
docker tag pdf-extractor:latest \
  ACCOUNT.dkr.ecr.REGION.amazonaws.com/pdf-extractor:latest

# Push to ECR
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/pdf-extractor:latest
```

---

## 📊 Event Flow

```
PDF Uploaded to S3
    ↓
S3 Event Notification
    ↓
SQS Queue
    ↓
Lambda Triggered
    ↓
PDF Extraction
    ↓
Result Upload to S3
    ↓
DynamoDB Update (optional)
    ↓
CloudWatch Logs
```

---

## ⚙️ Configuration

### Lambda Settings

```python
# config.py
LAMBDA_TIMEOUT = 900  # 15 minutes
LAMBDA_MEMORY = 1024  # MB
BATCH_SIZE = 10
VISIBILITY_TIMEOUT = 1800
```

### SQS Settings

```python
MAX_RECEIVE_COUNT = 3
MESSAGE_RETENTION = 14  # days
VISIBILITY_TIMEOUT = 900  # seconds
```

---

## 📊 IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:*:*:pdf-queue"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

## 🧪 Testing

### Local Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_extractor.py

# With coverage
pytest --cov=src
```

### Mock SQS

```python
import boto3
from moto import mock_sqs

@mock_sqs
def test_sqs_processing():
    sqs = boto3.client('sqs', region_name='us-east-1')
    
    # Create queue
    queue = sqs.create_queue(QueueName='test-queue')
    
    # Send message
    sqs.send_message(
        QueueUrl=queue['QueueUrl'],
        MessageBody='test message'
    )
    
    # Process
    messages = sqs.receive_message(QueueUrl=queue['QueueUrl'])
    assert len(messages['Messages']) == 1
```

---

## 📈 Monitoring

### CloudWatch Metrics

- Lambda invocations
- Errors and duration
- SQS messages processed
- S3 uploads

### CloudWatch Logs

View logs:

```bash
aws logs tail /aws/lambda/pdf-extractor --follow
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/Enhancement`)
3. Commit changes (`git commit -m 'Add Enhancement'`)
4. Push to branch (`git push origin feature/Enhancement`)
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Email: [saumay.killa@gmail.com](mailto:saumay.killa@gmail.com)

---

## 🔗 Links

- **GitHub**: [https://github.com/saumaykilla/pdf-extract-service-sqs](https://github.com/saumaykilla/pdf-extract-service-sqs)

---

<div align="center">

**Serverless PDF Processing at Scale**

Made with ❤️ by Saumay Killa

[⬆ back to top](#pdf-extract-service-sqs-)

</div>
