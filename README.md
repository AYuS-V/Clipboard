# Clipboard

/home/admin/Desktop/practice

curl -sO http://192.168.0.57:8080/jnlpJars/agent.jar;java -jar agent.jar -url http://192.168.0.57:8080/ -secret c3c279447bd9c6f3d4416185940f2c91283bf4ee98e393e3726465c84dcf6aaa -name Aayush -webSocket -workDir "/home/admin/Desktop/practice"


curl -sO http://192.168.0.57:8080/jnlpJars/agent.jar;java -jar agent.jar -url http://192.168.0.57:8080/ -secret a39af8160946ccae91eb50b656fd0ea18b515fc91e898d7393bd4e2c90122b4e -name aftab -webSocket -workDir "/home/shaikh-aftab/Desktop/jenkins"

https://github.com/themeselection/sneat-bootstrap-html-aspnet-core-mvc-admin-template-free.git/

[Unit]
Description=Nexus Repository Manager
After=network.target

[Service]
Type=forking
User=nexus
Group=nexus
ExecStart=/opt/nexus/bin/nexus start
ExecStop=/opt/nexus/bin/nexus stop
Restart=on-abort
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target



pipeline {
    agent any
    
    environment {
        GIT_REPO ='https://github.com/themeselection/sneat-bootstrap-html-aspnet-core-mvc-admin-template-free.git'
        GIT_BRANCH = 'main'
    }
    
    stages{
        stage('Clone Repo') {
            steps {
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }
        
        stage('Restore') {
            steps {
                sh 'dotnet restore'
            }
        }
        
        stage('Build') {
            steps {
                sh 'dotnet build'
            }
        }
    }
    
}
