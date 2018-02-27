node ('CAST-Analysis-Server') {
    stage ('CAST Analysis') {
        git credentialsId: '6fca6e6a-2db0-4c2d-abec-513591c993e7', url: 'https://github.com/prabinovich/CAST-Jenkins-Pipeline.git'
        dir('smallFibonacci') {
           git credentialsId: '1b132c46-025f-4c76-986d-91b3237c7c1f', url: 'https://gitlab.com/johnny2136/SmallFibonacci.git'
        }

        echo '-- Packaging and Delivery of Source Code --'
        bat '%WORKSPACE%\\CLI-Scripts\\CMS_AutomateDelivery.bat "profile=sandbox802" "app=SmallFibonacci" "fromVersion=v1" "version=version %BUILD_NUMBER%"'

        echo '-- Analyze Application --'
        bat '%WORKSPACE%\\CLI-Scripts\\CMS_Analyze.bat "profile=sandbox802" "app=SmallFibonacci"'

        echo '-- Generate Snapshot --'
        bat '%WORKSPACE%\\CLI-Scripts\\CMS_GenerateSnapshot.bat "profile=sandbox802" "app=SmallFibonacci" "version=version %BUILD_NUMBER%"'
    }
}

node ('Docker-Build-Box') {
   
   stage ('Get Code') {
        git credentialsId: '1b132c46-025f-4c76-986d-91b3237c7c1f', url: 'https://gitlab.com/johnny2136/SmallFibonacci.git'
   }
   
   stage ('Build App') {
        sh 'javac -d bin -cp "src/lib/*" src/fibo/Fibonacci.java src/fibo/FibonacciTest.java'
   }
   
   stage ('Unit Tests') {
       dir ("bin") {
            sh 'java -cp .:../src/lib/* org.junit.runner.JUnitCore fibo.FibonacciTest'
       }
   }
   
   stage ('Build Docker Image') {
       writeFile file: 'Dockerfile', 
        text: """
        #
        # Demo Dockerfile
        #
        FROM ubuntu:latest
        
        RUN apt-get update
        RUN apt-get install -y openjdk-8-jdk
        RUN apt-get install -y openssh-server
        
        RUN mkdir /var/run/sshd
        RUN echo 'root:CastAIP1234' | chpasswd
        RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
        
        # SSH login fix. Otherwise user is kicked off after login
        
        ENV NOTVISIBLE "in users profile"
        RUN echo "export VISIBLE=now" >> /etc/profile
        
        COPY bin/fibo/* /home/fibo/
        COPY bin/lib/* /home/lib/
        WORKDIR /home
        
        EXPOSE 22
        CMD ["/usr/sbin/sshd", "-D"]
        """
        
        sh "docker build -t prabinovich/smallfibonacci . "
   }

   stage ('Publish Docker Image') {
       sh "docker push prabinovich/smallfibonacci"
   }
}

node ('Docker-Deploy-Box') {
    stage ('Docker Cleanup') {
        sh "docker stop smallfibonacci || true"
        sh "docker rm smallfibonacci || true" 
        sh "docker rmi prabinovich/smallfibonacci || true"
    }
    
    stage ('Run Docker Container') {
        sh "docker run --detach=true -p 2222:22 --name smallfibonacci prabinovich/smallfibonacci" 
    } 
}
