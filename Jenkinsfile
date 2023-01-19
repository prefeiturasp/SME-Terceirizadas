pipeline {
    environment {
      branchname =  env.BRANCH_NAME.toLowerCase()
      kubeconfig = getKubeconf(env.branchname)
      registryCredential = 'jenkins_registry'
    }

    agent {
      node { label 'python-36-sigpae' }
    }

    options {
      buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
      disableConcurrentBuilds()
      skipDefaultCheckout()
    }

    stages {

        stage('CheckOut') {
            steps { checkout scm }
        }

        stage('AmbienteTestes') {
            agent { label 'master' }
            when { branch 'homolog' }
            steps {
                script {
                    CONTAINER_ID = sh (script: 'docker ps -q --filter "name=terceirizadas-db"',returnStdout: true).trim()
                    if (CONTAINER_ID) {
                        sh "echo nome é: ${CONTAINER_ID}"
                        sh "docker rm -f ${CONTAINER_ID}"
                        sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
                    }
                    else {
                        sh 'docker run -d --rm --cap-add SYS_TIME --name terceirizadas-db --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=terceirizadas -e POSTGRES_PASSWORD=adminadmin -e POSTGRES_USER=postgres postgres:9-alpine'
                    }
                }
            }
        }

        stage('AnaliseCodigo') {
	      when { branch 'homolog' }
          steps {
              withSonarQubeEnv('sonarqube-local'){
                sh 'echo "[ INFO ] Iniciando analise Sonar..." && sonar-scanner \
                -Dsonar.projectKey=SME-Terceirizadas \
                -Dsonar.sources=.'
            }
          }
        }

        stage('Testes') {
          when { branch 'homolog_' }
          steps {
             sh 'pip install --user pipenv==2022.4.8'
             sh 'pip install --user psycopg2'
             sh 'pipenv install --dev'
             sh 'pipenv run pytest'
             sh 'pipenv run flake8'
          }
          post {
            success{
              publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
            }
          }
        }

        stage('Build') {
          when { anyOf { branch 'master'; branch 'main'; branch "story/*"; branch 'development'; branch 'release'; branch 'homolog';  } }
          steps {
            script {
              imagename1 = "registry.sme.prefeitura.sp.gov.br/${env.branchname}/sme-sigpae-api"
              //imagename2 = "registry.sme.prefeitura.sp.gov.br/${env.branchname}/sme-outra"
              dockerImage1 = docker.build(imagename1, "-f Dockerfile .")
              //dockerImage2 = docker.build(imagename2, "-f Dockerfile_outro .")
              docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
              dockerImage1.push()
              //dockerImage2.push()
              }
              sh "docker rmi $imagename1"
              //sh "docker rmi $imagename2"
            }
          }
        }

        stage('Deploy'){
            when { anyOf {  branch 'master'; branch 'main'; branch 'development'; branch 'release'; branch 'homolog';  } }
            steps {
                script{
                    if ( env.branchname == 'main' ||  env.branchname == 'master' || env.branchname == 'homolog' || env.branchname == 'release' ) {
                        sendTelegram("🤩 [Deploy ${env.branchname}] Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nMe aprove! \nLog: \n${env.BUILD_URL}")

			    withCredentials([string(credentialsId: 'aprovadores-coresso-sigpae', variable: 'aprovadores')]) {
                            timeout(time: 24, unit: "HOURS") {
                                input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: "${aprovadores}"
                            }
                        }


                    }
                    if ( env.branchname == 'homolog' || env.branchname == 'release' ) {
                        withCredentials([file(credentialsId: "${kubeconfig}", variable: 'config')]){
                            sh('cp $config '+"$home"+'/.kube/config')
		            sh 'kubectl rollout restart deployment/sigpae-backend -n sme-sigpae-treino'
                            sh 'kubectl rollout restart deployment/sigpae-beat -n sme-sigpae-treino'
                            sh 'kubectl rollout restart deployment/sigpae-celery -n sme-sigpae-treino'
			    sh 'kubectl rollout restart deployment/sigpae-frontend -n sme-sigpae-treino'
                            sh('rm -f '+"$home"+'/.kube/config')
                        }
                    }
                    withCredentials([file(credentialsId: "${kubeconfig}", variable: 'config')]){
                            sh('cp $config '+"$home"+'/.kube/config')
                            sh 'kubectl rollout restart deployment/sigpae-backend -n sme-sigpae'
                            sh 'kubectl rollout restart deployment/sigpae-beat -n sme-sigpae'
                            sh 'kubectl rollout restart deployment/sigpae-celery -n sme-sigpae'
			    sh 'kubectl rollout restart deployment/sigpae-frontend -n sme-sigpae'
                            sh('rm -f '+"$home"+'/.kube/config')
                    }
                }
            }
        }
    }

  post {
    success { sendTelegram("🚀 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Success \nLog: \n${env.BUILD_URL}console") }
    unstable { sendTelegram("💣 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Unstable \nLog: \n${env.BUILD_URL}console") }
    failure { sendTelegram("💥 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Failure \nLog: \n${env.BUILD_URL}console") }
    aborted { sendTelegram ("😥 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Aborted \nLog: \n${env.BUILD_URL}console") }
  }
}
def sendTelegram(message) {
    def encodedMessage = URLEncoder.encode(message, "UTF-8")
    withCredentials([string(credentialsId: 'telegramToken', variable: 'TOKEN'),
    string(credentialsId: 'telegramChatId', variable: 'CHAT_ID')]) {
        response = httpRequest (consoleLogResponseBody: true,
                contentType: 'APPLICATION_JSON',
                httpMode: 'GET',
                url: 'https://api.telegram.org/bot'+"$TOKEN"+'/sendMessage?text='+encodedMessage+'&chat_id='+"$CHAT_ID"+'&disable_web_page_preview=true',
                validResponseCodes: '200')
        return response
    }
}
def getKubeconf(branchName) {
    if("main".equals(branchName)) { return "config_prd"; }
    else if ("master".equals(branchName)) { return "config_prd"; }
    else if ("homolog".equals(branchName)) { return "config_hom"; }
    else if ("release".equals(branchName)) { return "config_hom"; }
    else if ("development".equals(branchName)) { return "config_dev"; }
}
