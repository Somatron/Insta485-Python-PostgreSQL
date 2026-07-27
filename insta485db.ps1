# insta485db.ps1
# Stop execution on any error

# Stop on errors
# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
$ErrorActionPreference = "Stop"

$DB_NAME = "insta485db"
$VAR_UPLOADS = "var/uploads"
$SQL_UPLOADS = "sql/uploads"

# Add these lines:
$env:PGUSER = "postgres"
$env:PGPASSWORD = "1D0ll@rDVD"

#Sanity check command line options (tells us how to run the script)
function Show-Usage {
  Write-Output "Usage: .\insta485db.ps1 (create|destroy|reset|dump)"
}

if ($args.count -ne 1) { #$args holds an array of all arguements passed to the script, .Count takes how many arguements our user provided, -ne 1 is not equal to 1
  Show-Usage
  exit 1
} #basically script checks if user failed to provide EXACTLY 1 arguemnt

$Action = $args[0]

#check if database exists
function Test-DatabaseExists {
  #Runs psql to check database presense, suppressing standard error
  $result = psql -lqt 2>$null | ForEach-Object { $_.Split('|')[0].Trim() } | Where-Object { $_ -eq $DB_NAME}
  return [bool]$result
}

switch ($Action) {
  "create" {
    if (Test-DatabaseExists) {
      Write-Error "Error: database '$DB_NAME' already exists"
      exit 1
    }

    #Create database and uploads folder
    createdb $DB_NAME
    New-Item -ItemType Directory -Force -Path $VAR_UPLOADS | Out-Null

    #Run SQL Files
    psql -d $DB_NAME -f sql/schema.sql
    psql -d $DB_NAME -f sql/data.sql

    #Copy assets if directory exists
    if (Test-Path $SQL_UPLOADS) {
      Copy-Item -Path "$SQL_UPLOADS\*" -Destionation $VAR_UPLOADS -Recurse -Force
    }
  }

  "destroy" {
    dropdb --if-exists $DB_NAME
    if (Test-DatabaseExists) {
      Remove-Item -Path "var" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
  }

  "reset" {
    #drop and clean
    dropdb --if-exists $DB_NAME
    if (Test-Path "var") {
      Remove-Item -Path "var" -Recurse -Force -ErrorAction SilentlyContinue
    }

    
    #Re-create database and uploads folder
    createdb $DB_NAME
    New-Item -ItemType Directory -Force -Path $VAR_UPLOADS | Out-Null

    #Run SQL Files
    psql -d $DB_NAME -f sql/schema.sql
    psql -d $DB_NAME -f sql/data.sql

    #Copy assets if directory exists
    if (Test-Path $SQL_UPLOADS) {
      Copy-Item -Path "$SQL_UPLOADS\*" -Destionation $VAR_UPLOADS -Recurse -Force
    }
  }

  "dump" {
    if (-not (Test-DatabaseExists)) {
      Write-Error "Error: database '$DB_NAME' does not exist"
      exit 1
    }
    pg_dump $DB_NAME
  }

  Default {
    Show-Usage
    exit 1
  }
}