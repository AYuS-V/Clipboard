Playbook path : /etc/ansible/Playbooks/script.yml

- name: Stop IIS Application and Backup Files
  hosts: test_server
  vars: 
    Nexus_URL: ""
  tasks:

    - name: Stop IIS Application
      win_shell: |
        Import-Module WebAdministration
        Stop-WebAppPool -Name "dev-SpaceReserveServices-User Portal"
      register: stop_iis_result

    - name: Check if IIS Application stopped successfully
      debug:
        msg: "IIS Application stopped successfully"
      when: stop_iis_result.rc == 0
      
    - name: Check if Backup Folder exists
      win_stat:
        path: C:\BackupFolder
      register: backup_folder_status

    - name: Create Backup Folder 
      win_file:
        path: C:\BackupFolder
        state: directory
      when: not backup_folder_status.stat.exists

    - name: Backing up the old files
      win_copy:
        src: "{{ item }}"
        dest: C:\BackupFolder\
      with_items:
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.Development.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.QA.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\web.config

    - name: Backing up the logs folder
      win_copy:
        src: "{{ item }}" 
        dest: C:\BackupFolder\
        recurse: yes
      with_items:
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\logs
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\runtime

    - name: Deleting older build
      win_file: 
        path: C:\inetpub\wwwroot\SpaceReserveServices-User Portal
        state: absent

     - name: Check if build folder exist Folder exists
      win_stat:
        path: C:\Latest_Build
      register: latest_folder_status

    - name: Create Latest build Folder 
      win_file:
        path: C:\Latest_Build
        state: directory
      when: not latest_folder_status.stat.exists

    - name: Downloading from provided Nexus URL
      win_get_url:
        url: "{{ Nexus_URL }}"
        dest: C:\Latest_Build\latest_build.zip

    - name: Unzipping the artifact file
      win_unzip: 
        src: C:\Latest_Build\latest_build.zip
        dest: C:\Latest_Build\
        remote_src: yes

    - name: Copying the latest build into SpaceReserveServices-User Portal
      win_copy:
        src: C:\Latest_Build\
        dest: C:\inetpub\wwwroot\SpaceReserveServices-User Portal\
        remote_src: yes

    - name: Deleting the some of the new files which are stored in backup folder
      win_file:
        path: "{{ item }}"
        state: absent
      with_items: 
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.Development.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.QA.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\appsettings.json
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\web.config

    - name: Deleting some of the folders
      win_file:
        path: "{{ item }}"
        state: absent
      with_items:
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\logs
        - C:\inetpub\wwwroot\SpaceReserveService-User Portal\runtime

    - name: Copying the backup files into the main published code
      win_copy: 
        src: C:\BackupFolder\
        dest: C:\inetpub\wwwroot\SpaceReserveServices-User Portal\
        remote_src: yes

    - name: Restart the IIS application
      win_shell: |
        Import-Module WebAdministration
        Start-WebAppPool -Name "dev-SpaceReserveServices-User Portal"
      register: restart_iis_result
