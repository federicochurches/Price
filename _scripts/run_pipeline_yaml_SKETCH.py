#!/usr/bin/env python3
"""
run_pipeline_yaml.py · Pipeline wrapper con configuración centralizada YAML

Propuesta para W21+ — Ejecuta el pipeline W20 manteniendo estructura actual,
pero con CONFIG leída desde WEEK_CONFIG.yml en lugar de hardcodeado en cada script.

Uso:
    python3 run_pipeline_yaml.py WEEK_CONFIG_W21.yml
    
Resultado:
    - Lee WEEK, VOL_NUM, PERIODO, etc. desde YAML
    - Exporta como env vars
    - Ejecuta 6 pasos del pipeline automáticamente
    - Genera logs centralizados
"""

import yaml
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

# ── Cargar configuración YAML ──────────────────────────────────────────────────
def load_config(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# ── Generar env vars desde YAML ────────────────────────────────────────────────
def create_env_from_config(config):
    env = os.environ.copy()
    env.update({
        'WEEK': f"W{config['week']}",
        'VOL_NUM': str(config['vol_num']),
        'PERIODO': config['periodo'],
        'MES_AÑO': config['mes_año'],
        'FECHA_PUB': config['fecha_pub'],
        'PICKLE_RND': f"rnd_w{config['vol_num']}_data.pkl",
        'PICKLE_CR': f"cr_w{config['vol_num']}_data.pkl",
    })
    return env

# ── Ejecutar paso del pipeline ─────────────────────────────────────────────────
def run_step(step, config, env, log_file):
    print(f"\n{'='*80}")
    print(f"🔄 PASO: {step.upper()}")
    print(f"{'='*80}")
    
    scripts = {
        'calc_rnd': ['python3', 'calc_rnd.py'],
        'calc_cr': ['python3', 'calc_cr.py'],
        'render_rnd': ['bash', '-c', 'python3 render_rnd_p1.py && python3 render_rnd_p2.py && python3 render_rnd_p3.py'],
        'render_cr': ['bash', '-c', 'python3 render_cr_p1.py && python3 render_cr_p2.py && python3 render_cr_p3.py'],
        'assemble': ['bash', '-c', 'python3 assemble_rnd.py && python3 assemble_cr.py'],
        'excel': ['bash', '-c', 'python3 excel_rnd.py && python3 excel_cr.py'],
        'mail': ['python3', 'render_mail_v3.py'],
        'build_package': ['python3', 'build_package.py'],
    }
    
    if step not in scripts:
        print(f"❌ Paso desconocido: {step}")
        return False
    
    try:
        result = subprocess.run(
            scripts[step],
            cwd=config['paths']['project'],
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10 min timeout por paso
        )
        
        # Log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n{step}\n{'='*80}\n")
            f.write(result.stdout)
            if result.stderr:
                f.write(f"\nSTDERR:\n{result.stderr}\n")
        
        if result.returncode == 0:
            print(f"✅ {step} completado")
            return True
        else:
            print(f"❌ {step} falló")
            print(result.stderr[-500:] if result.stderr else result.stdout[-500:])
            return False
    
    except subprocess.TimeoutExpired:
        print(f"❌ {step} timeout (>10min)")
        return False
    except Exception as e:
        print(f"❌ {step} error: {e}")
        return False

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("❌ Uso: python3 run_pipeline_yaml.py WEEK_CONFIG.yml")
        sys.exit(1)
    
    config_file = sys.argv[1]
    if not Path(config_file).exists():
        print(f"❌ Archivo no encontrado: {config_file}")
        sys.exit(1)
    
    # Cargar configuración
    config = load_config(config_file)
    env = create_env_from_config(config)
    
    print(f"\n{'='*80}")
    print(f"🚀 PIPELINE W{config['week']} · {config['periodo']}")
    print(f"{'='*80}")
    print(f"Config: {config_file}")
    print(f"WEEK={env['WEEK']} VOL_NUM={env['VOL_NUM']}")
    
    # Log file
    log_file = Path(config['paths']['outputs']) / f"pipeline_w{config['vol_num']}.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Ejecutar pipeline
    steps = config.get('pipeline', [
        'calc_rnd', 'calc_cr', 'render_rnd', 'render_cr', 
        'assemble', 'excel', 'mail', 'build_package'
    ])
    
    failed_steps = []
    for i, step in enumerate(steps, 1):
        print(f"\n[{i}/{len(steps)}] Ejecutando {step}...")
        if not run_step(step, config, env, str(log_file)):
            failed_steps.append(step)
            if step in ['calc_rnd', 'calc_cr']:  # No continuar si fallan cálculos
                print(f"\n❌ Pipeline detenido: {step} es crítico")
                break
    
    # Resumen
    print(f"\n{'='*80}")
    if not failed_steps:
        print(f"✅ PIPELINE COMPLETADO · W{config['week']}")
        print(f"   ZIP: {config['paths']['outputs']}/Price_W{config['vol_num']}.zip")
        print(f"   Log: {log_file}")
    else:
        print(f"❌ PIPELINE CON ERRORES")
        print(f"   Pasos fallidos: {', '.join(failed_steps)}")
        print(f"   Log: {log_file}")
    print(f"{'='*80}\n")
    
    sys.exit(0 if not failed_steps else 1)

if __name__ == '__main__':
    main()
