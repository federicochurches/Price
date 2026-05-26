#!/usr/bin/env python3
"""
run_pipeline.py · Orquestador del pipeline Supply Optimization con config YAML

Uso:
    python3 run_pipeline.py WEEK_CONFIG.yml
    
Ejemplo:
    python3 run_pipeline.py WEEK_CONFIG_W21.yml

Características:
    - Lee configuración centralizada desde YAML
    - Exporta variables de entorno a todos los scripts
    - Ejecuta 6 pasos del pipeline automáticamente
    - Genera logs detallados con timestamps
    - Validación de datasets pre-ejecución
    - Rollback inteligente en caso de errores críticos
"""

import yaml
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# ── COLORES PARA SALIDA ────────────────────────────────────────────────────
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ── LOGGER ─────────────────────────────────────────────────────────────────
class PipelineLogger:
    def __init__(self, log_file):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.write_text("")  # Reset
        self.verbose = True
    
    def log(self, msg, level='INFO', color=None):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {level}: {msg}"
        
        # Print a consola
        if color:
            print(f"{color}{log_msg}{Colors.ENDC}")
        else:
            print(log_msg)
        
        # Write a archivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def info(self, msg):
        self.log(msg, 'INFO', Colors.OKBLUE)
    
    def success(self, msg):
        self.log(msg, 'SUCCESS', Colors.OKGREEN)
    
    def warning(self, msg):
        self.log(msg, 'WARNING', Colors.WARNING)
    
    def error(self, msg):
        self.log(msg, 'ERROR', Colors.FAIL)
    
    def section(self, msg):
        sep = '='*80
        print(f"\n{Colors.BOLD}{Colors.HEADER}{sep}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{msg.center(80)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{sep}{Colors.ENDC}\n")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{sep}\n{msg}\n{sep}\n")

# ── CARGAR CONFIGURACIÓN YAML ──────────────────────────────────────────────
def load_config(yaml_file):
    """Cargar y validar archivo YAML de configuración"""
    if not Path(yaml_file).exists():
        print(f"{Colors.FAIL}❌ Archivo no encontrado: {yaml_file}{Colors.ENDC}")
        sys.exit(1)
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        print(f"{Colors.FAIL}❌ Error parsing YAML: {e}{Colors.ENDC}")
        sys.exit(1)

# ── VALIDAR DATASETS PRE-EJECUCIÓN ────────────────────────────────────────
def validate_datasets(config, logger):
    """Verificar que los datasets existan antes de ejecutar"""
    logger.section("📊 VALIDACIÓN DE DATASETS")
    
    week = config['week']
    vol_num = str(config['vol_num'])
    uploads = Path(config['paths']['uploads'])
    project = Path(config['paths']['project'])
    
    datasets_required = {
        f'Dataset_RatesNoDispo_W{week}.xlsx': 'RND actual',
        f'Dataset_CheckRates_W{week}.xlsx': 'CR actual',
        f'Dataset_RatesNoDispo_W{week-1}.xlsx': 'RND anterior (WoW)',
        f'Dataset_CheckRates_W{week-1}.xlsx': 'CR anterior (WoW)',
    }
    
    all_exist = True
    for filename, desc in datasets_required.items():
        path_uploads = uploads / filename
        path_project = project / filename
        
        if path_uploads.exists():
            logger.success(f"✓ {filename} ({desc}) en /uploads")
        elif path_project.exists():
            logger.warning(f"⚠ {filename} ({desc}) en /project (fallback)")
        else:
            logger.error(f"✗ FALTA: {filename} ({desc})")
            all_exist = False
    
    if not all_exist:
        logger.error("❌ Datasets incompletos. Abortando.")
        sys.exit(1)
    
    logger.success("✅ Todos los datasets validados")

# ── CREAR VARIABLES DE ENTORNO ────────────────────────────────────────────
def create_env_vars(config, logger):
    """Generar variables de entorno desde YAML"""
    logger.section("🔧 CONFIGURACIÓN")
    
    env = os.environ.copy()
    
    week = config['week']
    vol_num = str(config['vol_num'])
    
    # Metadatos principales
    env_updates = {
        'WEEK': f"W{week}",
        'VOL_NUM': vol_num,
        'PERIODO': config['periodo'],
        'MES_AÑO': config['mes_año'],
        'FECHA_PUB': config.get('fecha_pub', ''),
        
        # Semana anterior (para WoW)
        'WEEK_PREV': f"W{config['week_prev']}",
        'VOL_NUM_PREV': str(config['vol_num_prev']),
        'PERIODO_PREV': config['periodo_prev'],
        
        # Pickles (nombres esperados)
        'PICKLE_RND': f"rnd_w{vol_num}_data.pkl",
        'PICKLE_CR': f"cr_w{vol_num}_data.pkl",
        
        # Rutas
        'PROJECT_DIR': config['paths']['project'],
        'OUTPUTS_DIR': config['paths']['outputs'],
        'UPLOADS_DIR': config['paths']['uploads'],
    }
    
    env.update(env_updates)
    
    # Log
    for key, val in env_updates.items():
        logger.info(f"{key}={val}")
    
    logger.success("✅ Variables de entorno configuradas")
    return env

# ── EJECUTAR PASO DEL PIPELINE ─────────────────────────────────────────────
def run_step(step_name, script_cmd, config, env, logger):
    """Ejecutar un paso individual del pipeline"""
    logger.section(f"🔄 PASO: {step_name.upper()}")
    
    # Ejecutar desde _scripts/ donde están los scripts
    project_dir = Path(config['paths']['project']) / '_scripts'
    
    # Comando a ejecutar
    if isinstance(script_cmd, str):
        # Comando shell (para pasos con múltiples scripts)
        cmd = ['bash', '-c', script_cmd]
    else:
        # Lista de comando + args
        cmd = script_cmd
    
    try:
        # Ejecutar con timeout
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=1200  # 20 min por paso
        )
        
        # Log stdout
        if result.stdout:
            with open(logger.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n--- STDOUT ---\n{result.stdout}\n")
            # Imprimir últimas líneas a consola
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                if line.strip():
                    print(f"  {line}")
        
        # Log stderr
        if result.stderr:
            with open(logger.log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n--- STDERR ---\n{result.stderr}\n")
        
        if result.returncode == 0:
            logger.success(f"✅ {step_name} completado")
            return True
        else:
            logger.error(f"❌ {step_name} falló (código {result.returncode})")
            if result.stderr:
                logger.error(f"Error: {result.stderr[-300:]}")
            return False
    
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {step_name} timeout (>20min)")
        return False
    except Exception as e:
        logger.error(f"❌ {step_name} excepción: {type(e).__name__}: {e}")
        return False

# ── PIPELINE STEPS ────────────────────────────────────────────────────────
def get_pipeline_steps(config):
    """Definir los 6 pasos del pipeline"""
    return [
        {
            'name': '1. CALC RND',
            'cmd': ['python3', 'calc_rnd.py'],
            'critical': True,  # Falla = abortar todo
        },
        {
            'name': '2. CALC CR',
            'cmd': ['python3', 'calc_cr.py'],
            'critical': True,
        },
        {
            'name': '3. RENDER RND + CR',
            'cmd': 'python3 render_rnd_p1.py && python3 render_rnd_p2.py && python3 render_rnd_p3.py && python3 render_cr_p1.py && python3 render_cr_p2.py && python3 render_cr_p3.py',
            'critical': True,
        },
        {
            'name': '4. ASSEMBLE UNIFICADO',
            'cmd': 'python3 assemble_unified.py',
            'critical': True,
        },
        {
            'name': '5. EXCEL RND + CR (consolidados)',
            'cmd': 'python3 excel_rnd.py && python3 excel_cr.py',
            'critical': False,  # No-critical: continuar aunque falle
        },
        {
            'name': '6. MAIL + HUB',
            'cmd': 'python3 render_mail_v3.py && python3 build_package.py',
            'critical': False,
        },
    ]

# ── MAIN ───────────────────────────────────────────────────────────────────
def main():
    # Validar argumentos
    if len(sys.argv) < 2:
        print(f"{Colors.FAIL}❌ Uso: python3 run_pipeline.py WEEK_CONFIG.yml{Colors.ENDC}")
        print(f"\nEjemplo:")
        print(f"  python3 run_pipeline.py WEEK_CONFIG_W21.yml")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Cargar config
    config = load_config(config_file)
    week = config['week']
    vol_num = str(config['vol_num'])
    
    # Logger
    log_file = Path(config['paths']['outputs']) / f"pipeline_W{week}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = PipelineLogger(log_file)
    
    # Banner inicial
    logger.section(f"🚀 PIPELINE SUPPLY OPTIMIZATION · W{week}")
    logger.info(f"Período: {config['periodo']}")
    logger.info(f"Config: {config_file}")
    logger.info(f"Log: {log_file}")
    
    # Validar datasets
    validate_datasets(config, logger)
    
    # Crear env vars
    env = create_env_vars(config, logger)
    
    # Ejecutar pipeline
    logger.section(f"▶️  INICIANDO PIPELINE · {len(get_pipeline_steps(config))} PASOS")
    
    steps = get_pipeline_steps(config)
    failed_steps = []
    
    for i, step in enumerate(steps, 1):
        logger.info(f"\n[{i}/{len(steps)}] Ejecutando: {step['name']}")
        
        success = run_step(
            step['name'],
            step['cmd'],
            config,
            env,
            logger
        )
        
        if not success:
            failed_steps.append(step['name'])
            if step['critical']:
                logger.error(f"\n❌ PIPELINE ABORTADO: {step['name']} es crítico")
                break
            else:
                logger.warning(f"⚠️  {step['name']} falló pero es non-critical, continuando...")
    
    # RESUMEN FINAL
    logger.section("📋 RESUMEN")
    
    if not failed_steps:
        logger.success(f"✅ PIPELINE COMPLETADO EXITOSAMENTE")
        logger.success(f"   Week: W{week}")
        logger.success(f"   Período: {config['periodo']}")
        logger.success(f"   ZIP: {config['paths']['outputs']}/Price_W{vol_num}.zip")
        logger.success(f"   Log: {log_file}")
        
        # Resumen JSON para integración
        summary = {
            'status': 'SUCCESS',
            'week': week,
            'vol_num': vol_num,
            'periodo': config['periodo'],
            'zip_path': f"{config['paths']['outputs']}/Price_W{vol_num}.zip",
            'log_path': str(log_file),
            'timestamp': datetime.now().isoformat(),
        }
        
        summary_file = Path(config['paths']['outputs']) / f"pipeline_W{week}_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        logger.success(f"   Summary JSON: {summary_file}")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ ¡LISTO PARA COMMIT A GITHUB!{Colors.ENDC}\n")
        return 0
    
    else:
        logger.error(f"❌ PIPELINE FALLÓ CON ERRORES")
        logger.error(f"   Pasos fallidos: {', '.join(failed_steps)}")
        logger.error(f"   Log: {log_file}")
        
        summary = {
            'status': 'FAILED',
            'week': week,
            'vol_num': vol_num,
            'failed_steps': failed_steps,
            'log_path': str(log_file),
            'timestamp': datetime.now().isoformat(),
        }
        
        summary_file = Path(config['paths']['outputs']) / f"pipeline_W{week}_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ Revisar logs para detalles{Colors.ENDC}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
