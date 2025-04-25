import os
import sys
import csv
import asyncio

from pydantic import BaseModel, Field, HttpUrl, ValidationError, SecretStr
from pydantic_core import PydanticCustomError
from scripts.models import InputRow, OutputRow
from typing import List, Optional, Dict, Any
from browser_use.agent.views import AgentHistoryList
from scripts.agent import get_agent


async def process_row(input_row: InputRow, output_dir: str) -> OutputRow:
	print(f"\n  Processing site: {input_row.siteName} ({input_row.siteURL})")
	try:
		agent, browser = get_agent(input_row, output_dir)
		history: AgentHistoryList = await agent.run(max_steps=10)
		# await browser.close()

		if history.is_done() and history.is_successful():
			print(f"  Processed {input_row.siteName}")
			return OutputRow(
				siteName=input_row.siteName,
				siteURL=input_row.siteURL,
				status="Success",  # No failure
			)
		else:
			errors_list = history.errors()
			errors = '-'.join(filter(None, errors_list))
			print(f"  Error processing {input_row.siteName}: {errors}")
			return OutputRow(
				siteName=input_row.siteName,
				siteURL=input_row.siteURL,
				status=f"Failed: {errors}",  # No failure
			)

	except Exception as e:
		print(f"  Error processing {input_row.siteName}: {e}", file=sys.stderr)
		return OutputRow(
			siteName=input_row.siteName,
			siteURL=input_row.siteURL,
			status=f"Failed: {e}",  # Capture the error message
		)


def setup_directories(script_dir: str, input_dir: str, output_dir: str, output_sub_dir: str):
	input_path = os.path.join(script_dir, input_dir)
	output_path = os.path.join(script_dir, output_dir)
	sub_dir_path = os.path.join(output_path, output_sub_dir)
	os.makedirs(input_path, exist_ok=True)

	if os.path.exists(output_path):
		if not os.path.isdir(output_path):
			raise FileExistsError(
				f"Output path '{output_path}' exists but is not a directory. "
				"Please remove the existing file/item or choose a different output path."
			)

	try:
		os.makedirs(output_path, exist_ok=True)
		os.makedirs(sub_dir_path, exist_ok=True)

	except Exception as e:
		raise IOError(f"Error creating output directory '{output_path}': {e}")

	return input_path, output_path


def get_input_filepath(input_dir: str, filename: str) -> str:
	return os.path.join(input_dir, filename)


def get_output_dirpath(output_dir: str, sub_dir: str) -> str:
	return os.path.join(output_dir, sub_dir)


def get_output_filepath(output_dir: str, file_name: str) -> str:
	return os.path.join(output_dir, file_name)


def read_csv(filepath: str) -> List[Dict[str, str]]:
	if not os.path.exists(filepath):
		raise FileNotFoundError(f"Input file not found: {filepath}")

	try:
		with open(filepath, mode="r", encoding="utf-8") as infile:
			reader = csv.DictReader(infile)
			return list(reader)
	except Exception as e:
		raise IOError(f"Error reading CSV file {filepath}: {e}")


def validate_rows(rows_data: List[Dict[str, str]]) -> List[InputRow]:
	validated_rows: List[InputRow] = []
	validation_errors: List[str] = []
	caught_validation_error: 'ValidationError' | None = None

	for i, row_data in enumerate(rows_data, start=2):
		try:
			validated_row = InputRow.model_validate(row_data)
			validated_rows.append(validated_row)
		except ValidationError as e:
			caught_validation_error = e
			errors = e.errors()
			for error in errors:
				field = error.get("loc", ["unknown_field"])[0]
				msg = error.get("msg", "validation failed")
				validation_errors.append(f"Row {i}, Field '{field}': {msg}")

	if validation_errors:
		print("\n--- Validation Errors ---", file=sys.stderr)
		for err_msg in validation_errors:
			print(err_msg, file=sys.stderr)
		print("\n-------------------------", file=sys.stderr)
		raise caught_validation_error

	return validated_rows


def process_all_rows(
	validated_input_rows: List[InputRow], output_dir: str
) -> List[OutputRow]:
	output_rows: List[OutputRow] = []
	print("\n--- Starting Row Processing ---")

	for i, input_row in enumerate(
		validated_input_rows, start=2
	):  # Start from 2 for original CSV row number
		print(f"\nProcessing row {i} ({input_row.siteName})... ", end="", flush=True)
		# Run the async function synchronously
		output_row = asyncio.run(process_row(input_row, output_dir))
		output_rows.append(output_row)

		print(f"Processed row {i} ({output_row.status})... ", end="", flush=True)

	print("\n--- Finished Row Processing ---")
	return output_rows


def write_csv(filepath: str, data: List[OutputRow]):
	if os.path.exists(filepath):
		raise FileExistsError(f"Output file already exists, terminating: {filepath}")

	if hasattr(OutputRow.model_config, "csv_headers"):
		fieldnames = OutputRow.model_config["csv_headers"]
	else:
		fieldnames = list(OutputRow.model_fields.keys())

	try:
		with open(filepath, mode="w", newline="", encoding="utf-8") as outfile:
			writer = csv.DictWriter(outfile, fieldnames=fieldnames)

			writer.writeheader()
			for row in data:
				# Convert Pydantic model to dictionary for DictWriter
				writer.writerow(row.model_dump())
	except Exception as e:
		raise IOError(f"Error writing CSV file {filepath}: {e}")

