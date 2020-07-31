rg="p4-health-services-rg"
# appName="fitbit"
loginServer="containerregistrypcx.azurecr.io"
principalId=${AZURE_PRINCIPALID}
principalPw=${AZURE_PRINCIPALPW}

if [ $# -eq 2 ]
then
    appName="$1"
    aciDNSLabel=p4-services-$appName

    cmd="$2"

    echo "got appName: $appName, cmd: $cmd"

    if [ $2 == "tagpush" ]
    then
        docker tag gcr.io/data-science-258408/$appName $loginServer/$appName
        docker push $loginServer/$appName

    elif [ $2 == "create" ]
    then
        # echo "$principalId, $principalPw"
        az container create \
            --resource-group $rg \
            --name $appName \
            --image $loginServer/$appName \
            --cpu 1 --memory 1 \
            --registry-login-server $loginServer \
            --registry-username $principalId \
            --registry-password $principalPw \
            --dns-name-label $aciDNSLabel \
            --ports 80
    else
        echo "cmd not supported, either tagpush or create"
    fi

else
    echo "provide appName and cmd"
fi