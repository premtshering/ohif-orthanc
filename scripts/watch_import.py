import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

ORTHANC_URL = "http://pacs:8042"

def patient_exists_on_server(patient_id):
    response = requests.get(f"{ORTHANC_URL}/patients")
    if response.status_code == 200:
        patients = response.json()
        for patient in patients:
            if patient_id in patient['MainDicomTags'].get('PatientID', ''):
                return True
    return False

class DicomHandler(FileSystemEventHandler):
    def __init__(self):
        # self.orthanc_url = "http://0.0.0.0:8042"  # Changed from 0.0.0.0
        self.orthanc_url = "http://pacs:8042"
        
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.dcm'):
            # Get the full path structure
            relative_path = os.path.relpath(event.src_path, '/var/lib/orthanc/import')
            path_parts = relative_path.split(os.sep)
            
            # Extract patient/study/series info from path
            patient_id = path_parts[0] if len(path_parts) > 0 else None
            study_id = path_parts[1] if len(path_parts) > 1 else None
            series_id = path_parts[2] if len(path_parts) > 2 else None
            
            print(f"Processing: Patient={patient_id}, Study={study_id}, Series={series_id}")
            
            time.sleep(1)  # Wait for file to be completely written
            self.upload_to_orthanc(event.src_path)
        
        if os.path.isdir(event.src_path):
            for patient_dir in event.src_path.iterdir():
                if not patient_dir.is_dir():
                    continue

                patient_name = patient_dir.name
                patient_id = f"PAT{hash(patient_name) % 100000:05d}"

                print(f"\nProcessing patient: {patient_name}")

                # Process image files
                # Walk through the directory structure
                for dat_dir in patient_dir.iterdir():
                    if not dat_dir.is_dir():
                        continue
                        
                    # For each dat directory
                    for series_dir in dat_dir.iterdir():
                        if not series_dir.is_dir():
                            continue
                            
                        # For each series directory
                        for img_file in series_dir.glob('*.dcm'):
                            print(f"\nUploading image: {img_file.name}")

                            try:
                                time.sleep(1)  # Wait for file to be completely written
                                self.upload_to_orthanc(img_file)

                            except Exception as e:
                                print(f"Error uploading {img_file}: {str(e)}")
            

    def upload_to_orthanc(self, dicom_path):
            """
            Upload a DICOM file to Orthanc
            """
            try:
                with open(dicom_path, 'rb') as f:
                    response = requests.post(
                        # 'http://0.0.0.0:8042/instances',
                        "http://pacs:8042/instances",
                        auth=('mapdr', 'mapdr'),
                        data=f.read(),
                        headers={'Content-Type': 'application/dicom'}
                    )
                if response.status_code == 200:
                    print(f"Successfully uploaded {dicom_path}")
                    return True
                else:
                    print(f"Failed to upload {dicom_path}: {response.status_code}")
                    print(f"Response: {response.text}")
                    return False
            except Exception as e:
                print(f"Error uploading {dicom_path}: {str(e)}")
                return False


def monitor_directory(path):
    event_handler = DicomHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    print(f"Started monitoring directory: {path}")
    print("Watching for DICOM files in all subdirectories...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def upload_to_orthanc(dicom_path):
    """
    Upload a DICOM file to Orthanc
    """
    try:
        with open(dicom_path, 'rb') as f:
            response = requests.post(
                # 'http://0.0.0.0:8042/instances',
                "http://pacs:8042/instances",
                auth=('mapdr', 'mapdr'),
                data=f.read(),
                headers={'Content-Type': 'application/dicom'}
            )
        if response.status_code == 200:
            print(f"Successfully uploaded {dicom_path}")
            return True
        else:
            print(f"Failed to upload {dicom_path}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error uploading {dicom_path}: {str(e)}")
        return False
    
def process_directory(input_dir):
    """
    Process all NIfTI files in input directory
    """
    input_path = Path(input_dir)

    # Process each patient directory
    for patient_dir in input_path.iterdir():
        if not patient_dir.is_dir():
            continue

        patient_name = patient_dir.name
        patient_id = f"PAT{hash(patient_name) % 100000:05d}"

        print(f"\nProcessing patient: {patient_name}")

        if patient_exists_on_server(patient_id):
            print(f"Patient {patient_name} with ID {patient_id} already exists on the server. Skipping processing.")
            continue

        # Walk through the directory structure
        for dat_dir in patient_dir.iterdir():
            if not dat_dir.is_dir():
                continue

            # For each dat directory
            for series_dir in dat_dir.iterdir():
                if not series_dir.is_dir():
                    continue

                # For each series directory
                for img_file in series_dir.glob('*.dcm'):
                    try:
                        print(f"\nUploading image: {img_file.name}")
                        upload_to_orthanc(img_file)
                    except Exception as e:
                        print(f"Error uploading {img_file}: {str(e)}")
            
            # for img_file in dat_dir.glob('*.dcm'):
            #         try:
            #             print(f"\nUploading seg: {img_file.name}")
            #             upload_to_orthanc(img_file)
            #         except Exception as e:
            #             print(f"Error uploading {img_file}: {str(e)}")




if __name__ == "__main__":
    import_dir = "/var/lib/orthanc/import"
    # import_dir = "/Users/msi/Desktop/temp_outputs"
    process_directory(import_dir)
    # monitor_directory(import_dir)
