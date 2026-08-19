#Requires -PSEdition Core
#Requires -Version 7

Set-StrictMode -Version 3.0


function find_WoT {
    $prop = Get-ItemProperty -Path "HKCU:\Software\Classes\.wotreplay\shell\open\command"
    if (-not $prop) { return }

    $cmd = $prop.PSObject.Properties["(default)"].Value
    $cmd.Split(" ")[0].Replace('"', "")
}

$MODNAME = "VoiceOverriderNG"
$MODPATH = "PYmods"

$VERFILE = ".\build_data\GAME_VERSION"
$GAME_VERSION = Get-Content -Path $VERFILE -Raw


$WOTEXE = find_WoT
if ($WOTEXE -and (Test-Path $WOTEXE)) {
    $WOTDIR = $WOTEXE.Replace("\win64", "").Replace("\WorldOfTanks.exe", "")
}
else
{
    $WOTDIR = "D:\Software\Games\Windows\Wargaming.net\World_of_Tanks_NA"
    $WOTEXE = "$WOTDIR\WorldOfTanks.exe"
}


$WOT_MODDIR = "$WOTDIR\mods\$GAME_VERSION\$MODPATH"
$WOT_CONFDIR = "$WOTDIR\mods\configs\$MODPATH\$MODNAME"
$WOT_LOGFILE = "$WOTDIR\python.log"

$wot = $Null
$jobs = @()
Push-Location $PSScriptRoot
try {
    $conf_fname = "build_data\wotmods\$MODPATH\$MODNAME.json"

    Write-Host "Compiling..." -ForegroundColor Yellow
    $json = Get-Content -Path $conf_fname -Raw | ConvertFrom-Json
    foreach ($prop in $json.files.PSObject.Properties) {
	$path = $prop.value.substring(6)
	$dir = Split-Path -Parent $path
	$fname = Split-Path -LeafBase $path
	$dest = "build\$dir\\"

	$src = ""
	if ($fname -eq "**") {
	    $src = "source\$dir\\"
	}
	else
	{
	    $ext = Split-Path -Extension $path
	    if ($ext = ".pyc") {
		$src = "source\$dir\$fname.py"
	    }
	}
	
	if ($src -ne "") {
	    Write-Host $src -ForegroundColor Cyan
	    py -2 .\build_tools\compiler.py -f -q -d $dir -o $dest $src
	    if (-not $?) {
		Write-Host "Compiler failed" -ForegroundColor Red
		exit 1
	    }
	}
    }
    
    Write-Host "Packing wotmods..." -ForegroundColor Yellow
    $wotmod = "$MODPATH\$MODNAME.wotmod"
    Write-Host $wotmod -ForegroundColor Cyan
    py -2 .\build_tools\packer.py -f -q -v $VERFILE $conf_fname "build\wotmods\$wotmod"
    if (-not $?) {
        Write-Host "Packer wotmod failed" -ForegroundColor Red
        exit 1
    }
    
    $i18n_file = "source\scripts\client\gui\mods\mod_$MODNAME\i18n.py"
    if (Test-Path $i18n_file) {
	Write-Host "Converting i18n py -> json..." -ForegroundColor Yellow
	py -2 .\i18n2json.py $i18n_file > "res\configs\PYmods\$MODNAME\i18n\en.json"
    }

    Write-Host "Packing zips..." -ForegroundColor Yellow
    Write-Host "$MODNAME.zip" -ForegroundColor Cyan
    py -2 .\build_tools\packer.py -f -q -v $VERFILE "build_data\archives\$MODNAME.json" "build\archives\$MODNAME.zip"
    if (-not $?) {
        Write-Host "Packer zip failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Installing..." -ForegroundColor Yellow
    $Null = New-Item -Type Directory -Force $WOT_MODDIR
    $Null = New-Item -Type Directory -Force "$WOT_CONFDIR\i18n"
    Copy-Item -Path .\build\wotmods\$MODPATH\$MODNAME.wotmod -Destination $WOT_MODDIR
    Copy-Item -Path .\res\configs\$MODPATH\$MODNAME\i18n\*.* -Destination "$WOT_CONFDIR\i18n"
    if (-not (Test-Path "$WOT_CONFDIR\$MODNAME.json")) {
	Copy-Item -Path .\res\configs\$MODPATH\$MODNAME\$MODNAME.json `
	    -Destination "$WOT_CONFDIR\$MODNAME.json"
    }
    
    Write-Host "Running WoT..." -ForegroundColor Yellow

    Clear-Content -Path $WOT_LOGFILE
    $jobs += Start-Job -ScriptBlock {
	Get-Content -Path $using:WOT_LOGFILE -Tail 1 -Wait | Tee-Object -FilePath python.log
    }

    $wot = Start-Process -FilePath $WOTEXE -PassThru
    $wotPID = $wot.Id
    $jobs += Start-Job -ScriptBlock {
	Wait-Process -Id $using:wotPID
    }


    while (-not (Wait-Job -Any $jobs -Timeout 1)) {
	Receive-Job $jobs[0]
    }
}
finally
{
    Write-Host "Finally..." -ForegroundColor Yellow

    if ($wot -and -not $wot.HasExited) {
	$wot.CloseMainWindow()
	$wot.WaitForExit()
    }

    foreach ($job in $jobs) {
	Stop-Job $job
	Receive-Job $job
	Remove-Job $job
    }

    Pop-Location
}
