import os
"""
def fileCreation(course, video_id, transcript):
	try:
		with open(f"{video_id}.txt", "x") as file:
			for caption in transcript:
				#file.write(str(caption))
				file.write(f"{caption['start']}: {caption['text']}\n")
	except FileExistsError:
		print(f"Error: {video_id}.txt already exists.")

"""


def fileCreation(course, video_id, transcript):
	try:
		# Create the course folder if it doesn't exist
		os.makedirs(course, exist_ok=True)

		# Define the full path inside the course folder
		file_path = os.path.join(course, f"{video_id}.txt")

		# Try to create the file (exclusive creation mode)
		with open(file_path, "x") as file:
			file.write(f"http://youtube.com/watch?v={video_id}\n");
			for caption in transcript:
				file.write(f"{caption['start']}: {caption['text']}\n")

	except FileExistsError:
		print(f"Error: {file_path} already exists.")