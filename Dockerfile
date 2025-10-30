# Use AWS Lambda Python 3.13 as the base image
FROM public.ecr.aws/lambda/python:3.13
# Accept API key as a build argument
ARG GEMINI_AI_API_KEY
ARG GRAPHQL_ENDPOINT
ARG GRAPHQL_API_KEY
ENV GEMINI_API_KEY=$GEMINI_API_KEY
ENV GRAPHQL_ENDPOINT=$GRAPHQL_ENDPOINT
ENV GRAPHQL_API_KEY=$GRAPHQL_API_KEY


# Set working directory to the Lambda function root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .


# Set the CMD to your Lambda handler
CMD [ "lambda_function.lambda_handler" ]
