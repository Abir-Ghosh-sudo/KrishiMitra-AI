$base = "C:\Users\ABIR\OneDrive\Desktop\hacathon\KrishiMitra-AI\apps\api\src\krishimitra_api\schemas"
$files = @("farm.py","crop.py","disease.py","irrigation.py","pest.py","energy.py","predictions.py","sustainability.py","documents.py","feedback.py","simulation.py","whatsapp.py")
foreach($f in $files){
  $p = Join-Path $base $f
  if(Test-Path $p){
    $c = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
    $c = $c.Replace('""""','"""')
    [System.IO.File]::WriteAllText($p, $c, [System.Text.Encoding]::UTF8)
    Write-Host "fixed $f"
  }
}
