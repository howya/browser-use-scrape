import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pydantic import ValidationError
from scripts.models import InputRow, OutputRow
from scripts.processing import setup_directories, get_input_filepath, get_output_filepath, read_csv, validate_rows, process_all_rows, write_csv, get_output_dirpath

load_dotenv()

INPUT_DIR = "input"
OUTPUT_DIR = "output"
OUTPUT_SUB_DIR = str(int(time.time()))
INPUT_FILENAME = "source.csv"
OUTPUT_FILENAME = "output.csv"

def main():
	"""Main function to orchestrate the CSV processing workflow."""
	print("Setting up directories...")
	script_dir = os.path.dirname(os.path.abspath(__file__))
	input_dir, output_dir = setup_directories(script_dir, INPUT_DIR, OUTPUT_DIR, OUTPUT_SUB_DIR)
	input_filepath = get_input_filepath(input_dir, INPUT_FILENAME)
	output_dir_path = get_output_dirpath(output_dir, OUTPUT_SUB_DIR)
	output_filepath = get_output_filepath(output_dir_path, OUTPUT_FILENAME)

	print(f"Input file: {input_filepath}")
	print(f"Output file directory will be: {output_dir_path}")
	print(f"Output file will be: {output_filepath}")

	try:
		print("Reading input CSV...")
		rows_data = read_csv(input_filepath)
		print(f"Successfully read {len(rows_data)} rows.")
	except (FileNotFoundError, IOError) as e:
		print(f"Error reading input file: {e}", file=sys.stderr)
		sys.exit(1)

	try:
		print("Validating rows...")
		validated_rows = validate_rows(rows_data)
		print("All rows validated successfully.")
	except ValidationError:
		sys.exit(1)  # Terminate on validation errors

	print("Processing validated rows...")
	output_data = process_all_rows(validated_rows, output_dir_path)
	print(f"Finished processing. Generated {len(output_data)} output rows.")

	try:
		print(f"Writing output CSV to {output_filepath}...")
		write_csv(output_filepath, output_data)
		print("Output CSV written successfully.")
	except (FileExistsError, IOError) as e:
		print(f"Error writing output file: {e}", file=sys.stderr)
		sys.exit(1)

	print("\nScript finished successfully.")


if __name__ == "__main__":
	main()
