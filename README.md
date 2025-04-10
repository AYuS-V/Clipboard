- name: Stop IIS Application and Backup Files
  hosts: test_server
  vars: 
    Nexus_URL: "http://172.16.1.236:8081/service/rest/v1/search/assets/download?sort=version&direction=desc&repository=Space-Reserve&format=maven2&group=Space-Reserve&name=dev_spacereserveservices_user&version=1.0.0"
    site_name: "dev-SpaceReserveServices-User Portal"
  tasks:

    - name: Check if the IIS Application Pool is stopped
      win_shell: |
        Import-Module WebAdministration
        (Get-WebAppPoolState -Name "{{site_name}}").Value
      register: app_pool_state

    - name: Stop IIS Application if it is running
      win_shell: |
        Import-Module WebAdministration
        Stop-WebAppPool -Name "{{site_name}}"
      when: app_pool_state.stdout.strip() == "Started"
      register: stop_iis_result


    - name: Check if Backup Folder exists
      win_stat:
        path: C:\Backup
      register: backup_folder_status

    - name: Create Backup Folder 
      win_file:
        path: C:\Backup
        state: directory
      when: not backup_folder_status.stat.exists

    - name: Backing up the old files
      win_copy:
        src: "{{ item }}"
        dest: C:\Backup\
        remote_src: yes
      with_items:
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.Development.json
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.QA.json
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.json
        - C:\inetpub\wwwroot\{{site_name}}\web.config

    - name: Check if logs and runtimes folders exist
      win_stat:
        path: "{{ item }}"
      with_items:
        - C:\inetpub\wwwroot\{{site_name}}\logs
        - C:\inetpub\wwwroot\{{site_name}}\runtimes
      register: folder_status

    - name: Backing up the logs and runtimes folders
      win_copy:
        src: "{{ item.item }}" 
        dest: C:\Backup\
        recurse: yes
        remote_src: yes
      with_items: "{{ folder_status.results }}"
      when: item.stat.exists
        
    - name: Deleting older build
      win_file: 
        path: C:\inetpub\wwwroot\{{site_name}}
        state: absent
        

    - name: Check if latest build folder exists
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
        dest: C:\inetpub\wwwroot\{{site_name}}\
        remote_src: yes

    - name: Deleting some of the new files which are stored in backup folder
      win_file:
        path: "{{ item }}"
        state: absent
      with_items: 
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.Development.json
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.QA.json
        - C:\inetpub\wwwroot\{{site_name}}\appsettings.json
        - C:\inetpub\wwwroot\{{site_name}}\web.config

    - name: Deleting some of the folders
      win_file:
        path: "{{ item }}"
        state: absent
      with_items:
        - C:\inetpub\wwwroot\{{site_name}}\logs
        - C:\inetpub\wwwroot\{{site_name}}\runtimes

    - name: Copying the backup files into the main published code
      win_copy: 
        src: C:\BackupFolder\
        dest: C:\inetpub\wwwroot\{{site_name}}\
        remote_src: yes

    - name: Restart the IIS application
      win_shell: |
        Import-Module WebAdministration
        Start-WebAppPool -Name "{{site_name}}"
      register: restart_iis_result

    - name: Check if IIS Application restarted successfully
      debug:
        msg: "IIS Application has been restarted successfully."
      when: restart_iis_result.rc == 0
