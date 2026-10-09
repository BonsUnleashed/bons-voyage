"""Build the combined Forge mod from source. Python 3.11+ and JDK 17+.

Usage: python build_release.py --server /path/to/forge-server --jdk /path/to/jdk
The server supplies Forge 47.4.16 SRG libraries and the separately installed
Waystones 14.1.21, Balm 7.3.44 and Lithostitched 1.4.11 compile dependencies. None are bundled.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parent
VERSION='1.19.3'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--server',required=True,type=Path);parser.add_argument('--jdk',type=Path)
    args=parser.parse_args()
    javac=str(args.jdk/'bin'/('javac.exe' if os.name=='nt' else 'javac')) if args.jdk else 'javac'
    libs=sorted((args.server/'libraries').rglob('*.jar'),key=lambda p:(not p.name.endswith('-srg.jar'),str(p)))
    assert libs,'Forge libraries not found'
    deps=[]
    for prefix in ('balm-','waystones-','lithostitched-'):
        found=list((args.server/'mods').glob(prefix+'*.jar'));assert len(found)==1,(prefix,found);deps+=found
    generated=subprocess.run([sys.executable,str(ROOT/'gen/build.py')],cwd=ROOT/'gen',capture_output=True,text=True,encoding='utf-8')
    (ROOT/'build-data.log').write_text(generated.stdout+generated.stderr,encoding='utf-8')
    assert generated.returncode==0,generated.stderr[-5000:]
    classes=ROOT/'build/classes';classes.mkdir(parents=True,exist_ok=True)
    cmd=['-encoding','UTF-8','-proc:none','--release','17','-classpath',os.pathsep.join(str(p.resolve()) for p in libs+deps),'-d',str(classes),*[str(p) for p in sorted((ROOT/'src/main/java').rglob('*.java'))]]
    argfile=ROOT/'build/javac.args';argfile.write_text('\n'.join('"'+s.replace('\\','/')+'"' for s in cmd),encoding='utf-8')
    subprocess.run([javac,'@'+str(argfile)],check=True)
    data=ROOT/f'dist/waystone_ruins-{VERSION}-data.jar'
    with zipfile.ZipFile(data) as z: entries={n:z.read(n) for n in z.namelist() if n.startswith('data/') or n in ('pack.png','pack.mcmeta')}
    for p in classes.rglob('*.class'):entries[p.relative_to(classes).as_posix()]=p.read_bytes()
    entries['META-INF/mods.toml']=(ROOT/'mods.toml').read_bytes()
    entries['META-INF/MANIFEST.MF']=f'Manifest-Version: 1.0\nFMLModType: MOD\nImplementation-Version: {VERSION}\n\n'.encode()
    for n in ('LICENSE','NOTICE.md'):entries[n]=(ROOT/n).read_bytes()
    out=ROOT/'dist'/f'waystone_ruins-{VERSION}.jar'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(entries.items()):
            info=zipfile.ZipInfo(n,(2026,10,9,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(out) as z:assert z.testzip() is None
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    (ROOT/'build/build-result.json').write_text(json.dumps({'version':VERSION,'file':out.name,'sha256':digest,'dependencies':[{'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in deps]},indent=2),encoding='utf-8')
    print(out,digest)

if __name__=='__main__':main()
