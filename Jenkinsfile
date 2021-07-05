pipeline {
    environment {
      imagename = "registry.sme.prefeitura.sp.gov.br/sigpae/sme-sigpae-api"
      registryCredential = 'regsme'
    }
    agent {
      node {
        label 'python-36-rc'
	    }
    }

    options {
      buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
      disableConcurrentBuilds()
      skipDefaultCheckout()
    }

    stages {
        stage('BD') {
        agent {
        label 'master'
        }
        steps {
          script {
            CONTAINER_ID = sh (
            script: 'docker ps -q --filter "name=terceirizadas-db"',
            returnStdout: true
            ).trim()
             if (CONTAINER_ID) {
               sh "echo nome é: ${CONTAINER_ID}"
               sh "docker rm -f ${CONTAINER_ID}"
               sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
            } else {

                sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
            }
          }

        }
      }

       stage('CheckOut') {
        steps {
          checkout scm
        }
       }

       stage('Testes') {
        steps {

          sh 'pip install --user pipenv'
          sh 'pipenv install --dev'
          sh 'pipenv run pytest'
          sh 'pipenv run flake8'


        }
        post {
            success{
            //  Publicando arquivo de cobertura
                publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
            }
       }
      }

    stage('Analise codigo') {
	    when {
           branch 'homolog'
        }
        steps {
            sh 'echo "[ INFO ] Iniciando analise Sonar..." && sonar-scanner \
              -Dsonar.projectKey=SME-Terceirizadas \
              -Dsonar.sources=. \
              -Dsonar.host.url=http://sonar.sme.prefeitura.sp.gov.br \
              -Dsonar.login=0d279825541065cf66a60cbdfe9b8a25ec357226'
        }
    }

       stage('Build DEV') {
         when {
           branch 'development'
         }
        steps {
          sh 'echo build docker image desenvolvimento'
          script {
            dockerImage = docker.build imagename
            docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
                dockerImage.push('dev')
            }
          }
          sh "docker rmi $imagename:dev"
        }
       }

       stage('Deploy DEV') {
         when {
           branch 'development'
         }
        steps {          
          sh 'echo Deploy ambiente desenvolvimento'
          sh '''
          set +x
          sed -e "s/\\${RANCHER_URL}/$RANCHER_URL_DEV/" -e "s/\\${RANCHER_TOKEN}/$RANCHER_TOKEN_DEV/" $HOME/config_template > $HOME/.kube/config
          set -x
          '''
          sh 'kubectl rollout restart deployment/sigpae-backend -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-beat -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-celery -n sme-sigpae'
          sh 'rm -f $HOME/.kube/config'
        }
       }

       stage('Build HOM') {
         when {
           branch 'homolog'
         }
        steps {
          sh 'echo build docker image homologação'
          script {
            dockerImage = docker.build imagename
            docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
                dockerImage.push('homolog')
            }
          }
          sh "docker rmi $imagename:homolog"
        }
       }

        stage('Deploy HOM') {
         when {
           branch 'homolog'
         }
        steps {
          timeout(time: 24, unit: "HOURS") {
          // telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Requer uma aprovação para deploy !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n")
            input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: 'ollyver_ottoboni, kelwy_oliveira, rodolfo_lima, anderson_morais, luis_zimmermann, rodolpho_azeredo'
          }
          sh 'echo Deploying ambiente homologacao'
          sh '''
          set +x
          sed -e "s/\\${RANCHER_URL}/$RANCHER_URL_HOM/" -e "s/\\${RANCHER_TOKEN}/$RANCHER_TOKEN_HOM/" $HOME/config_template > $HOME/.kube/config
          set -x
          '''
          sh 'kubectl rollout restart deployment/sigpae-backend -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-beat -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-celery -n sme-sigpae'
          sh 'rm -f $HOME/.kube/config'                   
        }
       }

       stage('Build PROD') {
         when {
           branch 'master'
         }
        steps {
          sh 'echo build docker image produção'
          script {
            dockerImage = docker.build imagename
            docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
                dockerImage.push()
            }
          }
          sh "docker rmi $imagename:latest"
        }
       }

        stage('Deploy PROD') {
         when {
           branch 'master'
         }
        steps {
          timeout(time: 24, unit: "HOURS") {
          // telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Requer uma aprovação para deploy !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n")
            input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: 'ollyver_ottoboni, kelwy_oliveira, rodolfo_lima, anderson_morais'
          }
          sh 'echo Deploying ambiente produção'
          sh '''
          set +x
          sed -e "s/\\${RANCHER_URL}/$RANCHER_URL_PRD/" -e "s/\\${RANCHER_TOKEN}/$RANCHER_TOKEN_PRD/" $HOME/config_template > $HOME/.kube/config
          set -x
          '''
          sh 'kubectl rollout restart deployment/sigpae-backend -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-beat -n sme-sigpae'
	  sh 'kubectl rollout restart deployment/sigpae-celery -n sme-sigpae'
          sh 'rm -f $HOME/.kube/config'  
        }
       }
    }

  post {
    always {
      echo 'One way or another, I have finished'
    }
    success {
      telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME} - Esta ok !!!\n Consulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)\n\n Uma nova versão da aplicação esta disponivel!!!")
    }
    unstable {
      telegramSend("O Build ${BUILD_DISPLAY_NAME} <${env.BUILD_URL}> - Esta instavel ...\nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
    failure {
      telegramSend("${JOB_NAME}...O Build ${BUILD_DISPLAY_NAME}  - Quebrou. \nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
    changed {
      echo 'Things were different before...'
    }
    aborted {
      telegramSend("O Build ${BUILD_DISPLAY_NAME} - Foi abortado.\nConsulte o log para detalhes -> [Job logs](${env.BUILD_URL}console)")
    }
  }
}
