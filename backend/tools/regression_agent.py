import json
from openai import OpenAI
import pandas as pd
from models.regression_model import train as train_regressor
from models.classification_model import train as train_classifier
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  api_key=os.getenv("JDNFJCJDJSMAKXNSJSMXS"),
  base_url="https://openrouter.ai/api/v1"
  )
tools = [
  {
    "type": "function",
    "name": "train_regressor",
    "description": "Train a regression model from a CSV dataset using selected input columns and target column. Optionally one-hot encode categorical input features and standardize features/target values.",
    "parameters": {
      "type": "object",
      "properties": {
        "csv_file": {
          "type": "string",
          "description": "Local path to the uploaded CSV file."
        },
        "target_x_columns": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Column names used as input features."
        },
        "target_y_columns": {
          "type": "array",
          "items": {"type": "string"},
          "description": "Target column name for regression. Usually one column."
        },
        "need_scale": {
          "type": "boolean",
          "description": "Whether to standardize input features and target values."
        },
        "need_encode": {
          "type": "boolean",
          "description": "Whether to one-hot encode categorical input columns."
        }
      },
      "required": [
        "csv_file",
        "target_x_columns",
        "target_y_columns",
        "need_scale",
        "need_encode"
      ],
      "additionalProperties": False
    },
    "strict": True
  },
  {
    "type": "function",
    "name": "train_classifier",
    "description": "Train a classification model from a CSV file to predict a class, category, label, boolean value, or discrete group.",
    "parameters": {
      "type": "object",
      "properties": {
        "csv_file": {"type": "string"},
        "target_x_columns": {
          "type": "array",
          "items": {"type": "string"}
        },
        "target_y_columns": {
          "type": "array",
          "items": {"type": "string"}
        },
        "need_scale": {"type": "boolean"},
        "need_encode": {"type": "boolean"}
      },
      "required": [
        "csv_file",
        "target_x_columns",
        "target_y_columns",
        "need_scale",
        "need_encode"
      ],
      "additionalProperties": False
    },
    "strict": True
  },
  {
    "type": "function",
    "name": "predict_regressor",
    "description": "Generate continuous regression predictions using a trained model and prepared test input data. Optionally inverse-transform scaled predictions back to original target units.",
    "parameters": {
      "type": "object",
      "properties": {
        "model_id": {
          "description": "Trained regression model object or model identifier."
        },
        "X_test": {
          "description": "Prepared input feature data for prediction."
        },
        "scaler_y": {
          "description": "Optional target scaler used to inverse-transform predictions."
        }
      },
      "required": [
        "model",
        "X_test",
        "scaler_y"
      ],
      "additionalProperties": False
    },
    "strict": True
  }
]

def call_function(name, args):
  if name == "train":
    return train_regressor(**args)

  raise ValueError(f"Unknown function: {name}")


def run_agent(user_prompt, csv_file):
  df = pd.read_csv(csv_file)
  csv_sample = df.head(10).to_dict(orient="records")
  csv_summary = df.describe(include="all").to_dict()
  
  input_messages = [
    {
      "role": "system",
      "content": """
        You are an AutoML assistant.

        The user uploads a CSV and describes what model they want.

        Your job:
        1. Read the user's request.
        2. Inspect the CSV columns, dtypes, summary, and sample rows.
        3. Choose the correct X feature columns.
        4. Choose the correct y target column.
        5. You must choose exactly one of these three task types:
          - "classifier" (if the goal is to predict a category, label, or discrete group) with train_classifier
          - "regressor" (if the goal is to predict a continuous numerical value or score) with train_regressor
          - "association" [CURRENTLY UNAVAILABLE] (if the goal is to find relationships, frequent patterns, or rules between items, with no single target column) with train_associtation

        Rules:
        - Use only column names that exist in the CSV.
        - Do not invent column names.
        - Do not use the target y column as an X feature.
        - Use need_encode=True if any selected X column is categorical/text.
        - Use need_scale=True when numeric features have very different ranges.

      """
    },
    {
      "role": "user",
      "content": f"""
        User request:
        {user_prompt}

        CSV file path:
        {csv_file}

        CSV columns:
        {df.columns.tolist()}

        CSV sample rows:
        {json.dumps(csv_sample, indent=2, default=str)}

        Dataset summary:
        {json.dumps(csv_summary, indent=2, default=str)}
      """
    }
  ]
  # print(input_messages)
  response = None
  for attempt in range(5):
    try:
      response = client.responses.create(
        model="openai/gpt-oss-120b:free",
        input=input_messages,
        tools=tools
      )
      break
    except:
      continue
  
  if not response:
    return "Fail to connect LLM"
  print(response.output)
  for item in response.output:
    
    if item.type != "function_call":
      continue
    
    print(input_messages)
    
    args = json.loads(item.arguments)
    if item.name == "train_regressor":
      result = train_regressor(**args)
    elif item.name == "train_classifier":
      result = train_classifier(**args)


    input_messages.append(item)
    input_messages.append({
      "type": "function_call_output",
      "call_id": item.call_id,
      "output": json.dumps(result, default=str)
    })

  final_response = None
  
  # Attempt 5 times due to rate limit error
  for i in range(5):
    try:
      final_response = client.responses.create(
        model="openai/gpt-oss-120b:free",
        input=input_messages,
        tools=tools
      )
      break
    except:
      continue
    
    

  return final_response.output_text if final_response else "can't connect to model"

prompt = """
Can you use your regression skills to predict the age of a possum? 
"""

print(run_agent(prompt, "/Users/minhquang/Desktop/SS 2026/No-Code-ML-Models-generator/backend/models/possum.csv"))