param(
    [Parameter(Mandatory=$true)][string]$MavenPath,
    [Parameter(Mandatory=$true)][string]$RepositoryPath,
    [Parameter(Mandatory=$true)][string]$OutputRoot
)
# Chạy sau benchmark, không làm tải nền trong cửa sổ đo mạng.
# Mỗi attempt lưu XML/log riêng, không dừng hoặc bỏ attempt khi test fail.
$ErrorActionPreference='Stop'
$experimentRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
Set-Location $experimentRoot
$experimentSelection='RuntimeContractTest,StabilityLifecycleTest,SessionWriterTest,TransportStabilityTest,ClientStabilityTest,MovementDemoProcessTest,LobbyLifecycleTest'
foreach($experimentAttempt in 1..3){
    $experimentDir=Join-Path $OutputRoot ('r'+$experimentAttempt.ToString('00'))
    if(Test-Path -LiteralPath $experimentDir){throw "Attempt already exists: $experimentDir"}
    New-Item -ItemType Directory -Path $experimentDir -Force | Out-Null
    $experimentStart=Get-Date
    $experimentStart.ToString('o') | Set-Content (Join-Path $experimentDir 'started-at.txt')
    # Native stderr vẫn được giữ trong log; không dùng -Dtest khác nhau qua các lần lặp.
    $ErrorActionPreference='Continue'
    & $MavenPath '-o' "-Dmaven.repo.local=$RepositoryPath" "-Dtest=$experimentSelection" test *> (Join-Path $experimentDir 'maven.log')
    $experimentExit=$LASTEXITCODE
    $ErrorActionPreference='Stop'
    $experimentExit | Set-Content (Join-Path $experimentDir 'exit-code.txt')
    (Get-Date).ToString('o') | Set-Content (Join-Path $experimentDir 'finished-at.txt')
    New-Item -ItemType Directory -Path (Join-Path $experimentDir 'surefire') | Out-Null
    $experimentSuites=@()
    foreach($experimentFile in (Get-ChildItem target/surefire-reports -Filter 'TEST-*.xml')){
        if($experimentFile.LastWriteTime -lt $experimentStart){continue}
        Copy-Item -LiteralPath $experimentFile.FullName -Destination (Join-Path $experimentDir "surefire/$($experimentFile.Name)")
        [xml]$experimentXml=Get-Content -Raw -Encoding UTF8 $experimentFile.FullName
        $experimentSuite=$experimentXml.testsuite
        $experimentSuites+=@{name=[string]$experimentSuite.name;tests=[int]$experimentSuite.tests;failures=[int]$experimentSuite.failures;errors=[int]$experimentSuite.errors;skipped=[int]$experimentSuite.skipped;cases=@($experimentSuite.testcase | ForEach-Object {@{name=[string]$_.name;status=if($_.failure){'FAIL'}elseif($_.error){'ERROR'}elseif($_.skipped){'SKIP'}else{'PASS'}}})}
    }
    @{selection=$experimentSelection;exit_code=$experimentExit;suites=$experimentSuites} | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $experimentDir 'junit-summary.json')
    foreach($experimentName in @('m1-server-process.log','m1-client-a-process.log','m1-client-b-process.log')){
        if(Test-Path "target/$experimentName"){
            $experimentFile=Get-Item "target/$experimentName"
            if($experimentFile.LastWriteTime -ge $experimentStart){Copy-Item -LiteralPath $experimentFile.FullName -Destination (Join-Path $experimentDir $experimentName)}
        }
    }
    Write-Output "$experimentDir exit=$experimentExit suites=$($experimentSuites.Count)"
}
