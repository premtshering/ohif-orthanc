## Docker Compose File for OHIF with ORTHANC

**Ohif:** (OHIF) Viewer is an open source, web-based, medical imaging platform.

**Orthanc:** Its free and open-source, lightweight DICOM server for medical imaging.

### Clone This Repo
> cd /ohif-orthanc
> docker-compose up -d

### Access OHIF and Orthanc

![Ohif viewer](./ohif-orthanc.jpg)

1. To access `OHIF` go to address `http://server-ip:3000`. 
2. To access `ORTHANC` webpage go to address `http://server-ip:8042`

> Default Username is `mapdr` & password is `changestrongpassword`


### Import DICOM Studies
1. You can directly Import DICOM files or Folder from OHIF.
2. You can directly send images from existing PACS/Machine
	 - AE: MAPDR
	 - PORT: 4242
	 - IP: your-server-ip
3. If you have file locally install httplib2 with pip.