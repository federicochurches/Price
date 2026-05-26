
var W={mode:'cr',canasta:'global',view:'hotel',dim:'corp',reOpen:false};
var CR_CV={"global": {"ef": "93,15%", "cv": "1,57%", "band": "Revisar", "bbg": "#FED7AA", "bfg": "#C2410C", "col": "#333132", "kv_id": "w21-kv-ef", "kv2_id": "w21-kv-cv", "hist_id": "w21-hist-ef", "hist2_id": "w21-hist-cv"}, "b2c": {"ef": "91,2%", "cv": "0,94%", "band": "Revisar", "bbg": "#FED7AA", "bfg": "#C2410C", "col": "#EA0074", "kv_id": "w21-kv-ef", "kv2_id": "w21-kv-cv", "hist_id": "w21-hist-ef", "hist2_id": "w21-hist-cv"}, "op": {"ef": "90,1%", "cv": "1,87%", "band": "Revisar", "bbg": "#FED7AA", "bfg": "#C2410C", "col": "#FCB000", "kv_id": "w21-kv-ef", "kv2_id": "w21-kv-cv", "hist_id": "w21-hist-ef", "hist2_id": "w21-hist-cv"}, "cug": {"ef": "94,8%", "cv": "2,31%", "band": "Aceptable", "bbg": "#FEF9C3", "bfg": "#713F12", "col": "#4FC3F4", "kv_id": "w21-kv-ef", "kv2_id": "w21-kv-cv", "hist_id": "w21-hist-ef", "hist2_id": "w21-hist-cv"}};
var RND_CV={"global": {"ef": "2,63%", "cv": "$834", "band": "Exitosa", "bbg": "#E1F5EE", "bfg": "#1A6B4A", "col": "#333132"}, "b2c": {"ef": "3,31%", "cv": "$248", "band": "Revisar", "bbg": "#FED7AA", "bfg": "#C2410C", "col": "#FCB000"}, "op": {"ef": "2,24%", "cv": "$688", "band": "Exitosa", "bbg": "#E1F5EE", "bfg": "#1A6B4A", "col": "#4FC3F4"}, "cug": {"ef": "2,82%", "cv": "$787", "band": "Exitosa", "bbg": "#E1F5EE", "bfg": "#1A6B4A", "col": "#EA0074"}};
var CR_D={"global": {"re": [{"n": "93,15%", "t": "Eficacia global \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "Target \u2265 97% \u00b7 mejora +0,19pp WoW."}, {"n": "1,57%", "t": "Conv Rate global \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "Mejora +0,06pp."}, {"n": "220", "t": "Hoteles <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+</b>", "d": "26% del P80."}, {"n": "186", "t": "Hoteles <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "22% sin convertir."}, {"n": "203", "t": "ConvRate <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "ConvRate < 0,8%."}, {"n": "72,1%", "t": "Marriott Canc\u00fan \u00b7 peor Eficacia", "d": "18.420 CR."}, {"n": "42.100", "t": "IHG Hotels \u00b7 l\u00edder volumen", "d": "71,3%."}, {"n": "0,8%", "t": "Hyatt Ziva \u00b7 peor ConvRate", "d": "14.807 CR."}, {"n": "4.017", "t": "DoubleTree Sharm \u00b7 #1 Sin Conv", "d": "Hilton."}, {"n": "847", "t": "Hoteles P80 analizados", "d": "W22."}], "hotels": [["Marriott Canc\u00fan Resort", "#FCE4F1", "#99162B", "Cr\u00edtica", "18.420", "72,1%", "0,8%", false, "\u25bc1.2pp"], ["Hyatt Ziva Los Cabos", "#FCE4F1", "#99162B", "Cr\u00edtica", "14.807", "74,8%", "1,1%", false, "\u25bc0.8pp"], ["Hilton Playa del Carmen", "#FED7AA", "#C2410C", "Revisar", "12.310", "86,2%", "1,4%", true, "\u25b20.3pp"], ["Iberostar Cozumel", "#FED7AA", "#C2410C", "Revisar", "9.540", "88,0%", "1,6%", null, "\u2014"], ["Hard Rock Hotel Riviera", "#FEF9C3", "#713F12", "Aceptable", "8.230", "94,5%", "2,1%", true, "\u25b20.5pp"], ["Grand Velas Riviera Maya", "#E1F5EE", "#1A6B4A", "Exitosa", "7.100", "97,2%", "2,9%", true, "\u25b21.1pp"]], "dims": [["IHG Hotels & Resorts", "#FCE4F1", "#99162B", "Cr\u00edtica", "42.100", "71,3%", "0,9%", false, "\u25bc2.1pp"], ["Hilton Worldwide", "#FED7AA", "#C2410C", "Revisar", "38.540", "87,2%", "1,3%", null, "\u2014"], ["Marriott International", "#FEF9C3", "#713F12", "Aceptable", "31.200", "94,1%", "2,0%", true, "\u25b20.7pp"], ["Hyatt Hotels Corp.", "#E1F5EE", "#1A6B4A", "Exitosa", "18.900", "97,8%", "2,8%", true, "\u25b21.4pp"], ["HIC (Inclusive Coll.)", "#FED7AA", "#C2410C", "Revisar", "11.440", "88,5%", "1,5%", false, "\u25bc0.3pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Escalar IHG Hotels Canc\u00fan \u2014 18.420 CR.", "t": "Conectividad", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Revisar mapping Hyatt Ziva \u2014 0,8%.", "t": "Mapping", "p": "W22"}, {"c": "mp", "o": "federico.iglesias", "a": "Auditar Third Party < 85%.", "t": "Channel", "p": "W23"}, {"c": "", "o": "ricardop.perez", "a": "Cotizaci\u00f3n Hilton PDC.", "t": "Cotizaci\u00f3n", "p": "W23"}], "co": ["IHG \u00b7 escalamiento W21 \u00b7 pendiente", "Marriott B2C \u00b7 auditor\u00eda en curso"]}, "b2c": {"re": [{"n": "91,2%", "t": "Eficacia B2C \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "-0,12pp WoW."}, {"n": "0,94%", "t": "Conv Rate B2C \u00b7 <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "Bajo target."}, {"n": "140", "t": "B2C <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+</b>", "d": "45% P80."}, {"n": "62", "t": "B2C <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "20%."}, {"n": "98", "t": "ConvRate <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b> B2C", "d": "Canal directo."}, {"n": "68,4%", "t": "Riu Palace \u00b7 peor Ef.", "d": "9.310 CR."}, {"n": "18.200", "t": "RIU Hotels \u00b7 l\u00edder B2C", "d": "69,5%."}, {"n": "0,7%", "t": "Iberostar Para\u00edso \u00b7 peor CV", "d": "7.200 CR."}, {"n": "3.100", "t": "Barcel\u00f3 Turquesa \u00b7 Sin Conv", "d": "Barcel\u00f3."}, {"n": "312", "t": "Hoteles P80 B2C", "d": "W22."}], "hotels": [["Hotel Riu Palace Canc\u00fan", "#FCE4F1", "#99162B", "Cr\u00edtica", "9.310", "68,4%", "0,7%", false, "\u25bc1.8pp"], ["Iberostar Para\u00edso Beach", "#FCE4F1", "#99162B", "Cr\u00edtica", "7.200", "71,1%", "0,9%", false, "\u25bc1.0pp"], ["Sandos Caracol Eco Resort", "#FED7AA", "#C2410C", "Revisar", "5.840", "86,7%", "1,2%", true, "\u25b20.2pp"], ["Fiesta Americana Coral", "#FED7AA", "#C2410C", "Revisar", "4.110", "89,3%", "1,5%", null, "\u2014"], ["Moon Palace Golf & Spa", "#FEF9C3", "#713F12", "Aceptable", "3.780", "95,0%", "2,0%", true, "\u25b20.6pp"]], "dims": [["RIU Hotels", "#FCE4F1", "#99162B", "Cr\u00edtica", "18.200", "69,5%", "0,8%", false, "\u25bc1.5pp"], ["Iberostar Group", "#FCE4F1", "#99162B", "Cr\u00edtica", "14.100", "73,2%", "1,0%", false, "\u25bc0.9pp"], ["Palace Resorts", "#FED7AA", "#C2410C", "Revisar", "9.400", "88,1%", "1,3%", null, "\u2014"], ["Barcel\u00f3 Hotels", "#FEF9C3", "#713F12", "Aceptable", "7.300", "94,7%", "1,9%", true, "\u25b20.5pp"], ["Sandos Hotels", "#E1F5EE", "#1A6B4A", "Exitosa", "4.100", "97,5%", "2,7%", true, "\u25b21.2pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Escalar RIU Hotels B2C.", "t": "Conectividad", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Revisar pricing Iberostar \u2014 0,7%.", "t": "Pricing", "p": "W22"}], "co": ["RIU Hotels B2C \u00b7 contratos W21 \u00b7 pendiente"]}, "op": {"re": [{"n": "90,1%", "t": "Eficacia B2B-OP \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "-0,31pp \u00b7 peso 0,6."}, {"n": "1,87%", "t": "Conv Rate B2B-OP \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "+0,14pp."}, {"n": "182", "t": "B2B-OP <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+</b>", "d": "29% P80."}, {"n": "98", "t": "B2B-OP <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "16%."}, {"n": "124", "t": "ConvRate <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b> OP", "d": "Peso 0,6."}, {"n": "65,3%", "t": "Westin Canc\u00fan \u00b7 peor Ef.", "d": "22.100 CR."}, {"n": "52.300", "t": "Marriott Intl \u00b7 l\u00edder OP", "d": "66,1%."}, {"n": "1,2%", "t": "Dreams Riviera \u00b7 peor CV", "d": "17.400 CR."}, {"n": "8.400", "t": "Hyatt Regency \u00b7 Sin Conv", "d": "Urgente."}, {"n": "628", "t": "Hoteles P80 B2B-OP", "d": "W22."}], "hotels": [["Westin Canc\u00fan Resort", "#FCE4F1", "#99162B", "Cr\u00edtica", "22.100", "65,3%", "1,2%", false, "\u25bc2.3pp"], ["Dreams Riviera Canc\u00fan", "#FCE4F1", "#99162B", "Cr\u00edtica", "17.400", "70,8%", "1,5%", false, "\u25bc1.1pp"], ["Paradisus Canc\u00fan", "#FED7AA", "#C2410C", "Revisar", "13.200", "84,5%", "1,8%", true, "\u25b20.4pp"], ["Now Jade Riviera", "#FED7AA", "#C2410C", "Revisar", "10.800", "87,2%", "2,0%", null, "\u2014"], ["Excellence Riviera", "#FEF9C3", "#713F12", "Aceptable", "8.600", "95,1%", "2,4%", true, "\u25b20.8pp"]], "dims": [["Marriott International", "#FCE4F1", "#99162B", "Cr\u00edtica", "52.300", "66,1%", "1,1%", false, "\u25bc1.9pp"], ["Meli\u00e1 Hotels", "#FED7AA", "#C2410C", "Revisar", "41.100", "85,3%", "1,7%", false, "\u25bc0.4pp"], ["Barcel\u00f3 Hotels", "#FEF9C3", "#713F12", "Aceptable", "28.700", "93,8%", "2,2%", true, "\u25b20.6pp"], ["AMR Collection", "#FEF9C3", "#713F12", "Aceptable", "19.400", "95,6%", "2,3%", true, "\u25b20.9pp"], ["Karisma Hotels", "#E1F5EE", "#1A6B4A", "Exitosa", "11.200", "97,9%", "3,1%", true, "\u25b21.8pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Escalar Marriott OP Canc\u00fan \u2014 52.300 CR.", "t": "Conectividad", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Auditar Dreams Riviera \u2014 1,2%.", "t": "Pricing", "p": "W22"}, {"c": "mp", "o": "federico.iglesias", "a": "Mapping Hyatt Regency \u2014 8.400 Sin Conv.", "t": "Mapping", "p": "W22"}], "co": ["Marriott B2B-OP \u00b7 W20 \u00b7 seguimiento"]}, "cug": {"re": [{"n": "94,8%", "t": "Eficacia CUG \u00b7 <b class=\"sev-badge\" style=\"background:#FEF9C3;color:#713F12;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Aceptable</b>", "d": "Mejor de los tres."}, {"n": "2,31%", "t": "Conv Rate CUG \u00b7 <b class=\"sev-badge\" style=\"background:#FEF9C3;color:#713F12;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Aceptable</b>", "d": "\u00danica > 2%."}, {"n": "46", "t": "CUG <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+</b>", "d": "25% P80."}, {"n": "18", "t": "CUG <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "10%."}, {"n": "34", "t": "ConvRate <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b> CUG", "d": "Luxury."}, {"n": "88,4%", "t": "Ritz-Carlton \u00b7 peor Ef.", "d": "6.800 CR."}, {"n": "12.400", "t": "Marriott Luxury \u00b7 l\u00edder CUG", "d": "88,9%."}, {"n": "1,8%", "t": "Belmond Maroma \u00b7 peor CV", "d": "5.100 CR."}, {"n": "1.800", "t": "Park Hyatt Aviara \u00b7 Sin Conv", "d": "Contractual."}, {"n": "184", "t": "Hoteles P80 CUG", "d": "W22."}], "hotels": [["The Ritz-Carlton Canc\u00fan", "#FED7AA", "#C2410C", "Revisar", "6.800", "88,4%", "1,8%", false, "\u25bc0.7pp"], ["Belmond Maroma Resort", "#FED7AA", "#C2410C", "Revisar", "5.100", "89,7%", "2,0%", null, "\u2014"], ["Rosewood Mayakoba", "#FEF9C3", "#713F12", "Aceptable", "4.300", "93,2%", "2,3%", true, "\u25b20.3pp"], ["Fairmont Mayakoba", "#FEF9C3", "#713F12", "Aceptable", "3.800", "94,9%", "2,5%", true, "\u25b20.5pp"], ["Banyan Tree Mayakoba", "#E1F5EE", "#1A6B4A", "Exitosa", "2.900", "97,8%", "3,2%", true, "\u25b21.4pp"]], "dims": [["Marriott Luxury Coll.", "#FED7AA", "#C2410C", "Revisar", "12.400", "88,9%", "1,9%", false, "\u25bc0.5pp"], ["Belmond", "#FEF9C3", "#713F12", "Aceptable", "10.100", "93,5%", "2,2%", null, "\u2014"], ["Rosewood Hotels", "#FEF9C3", "#713F12", "Aceptable", "8.700", "95,1%", "2,6%", true, "\u25b20.4pp"], ["Four Seasons", "#E1F5EE", "#1A6B4A", "Exitosa", "6.200", "97,4%", "3,0%", true, "\u25b21.1pp"], ["Banyan Tree", "#E1F5EE", "#1A6B4A", "Exitosa", "3.800", "98,2%", "3,5%", true, "\u25b22.1pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Revisar Ritz-Carlton CUG \u2014 88,4%.", "t": "Contractual", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Ajustar Belmond Maroma \u2014 1,8%.", "t": "Pricing", "p": "W23"}], "co": ["Park Hyatt Aviara CUG \u00b7 diagn\u00f3stico W21"]}};
var RND_D={"global": {"re": [{"n": "2,63%", "t": "NoDispo global \u00b7 <b class=\"sev-badge\" style=\"background:#E1F5EE;color:#1A6B4A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Exitosa</b>", "d": "Por debajo del 5% \u00b7 mejora vs W20."}, {"n": "$834", "t": "IPM global \u00b7 <b class=\"sev-badge\" style=\"background:#FEF9C3;color:#713F12;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Aceptable</b>", "d": "Target \u2265 $650 \u00b7 r\u00e9cord de las \u00faltimas 5 semanas."}, {"n": "131", "t": "Hoteles P80 <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+ NoDispo</b>", "d": "NoDispo > 20%."}, {"n": "247", "t": "Hoteles P80 <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conversi\u00f3n</b>", "d": "Sin booking \u00b7 BKGS=0."}, {"n": "0,25%", "t": "Canal B2C NoDispo m\u00e1s alto", "d": "Canal directo con mayor demanda perdida."}, {"n": "3,31%", "t": "B2C \u00b7 mayor NoDispo global", "d": "Mayor brecha de los tres canales."}, {"n": "$834", "t": "CUG \u00b7 mayor IPM", "d": "Canal privado lidera revenue por mill\u00f3n."}, {"n": "$248", "t": "B2C \u00b7 menor IPM", "d": "Canal directo pierde revenue vs canal opaco."}, {"n": "Canc\u00fan", "t": "Destino con mayor NoDispo", "d": "Primera prioridad de apertura de cupos."}, {"n": "1.342", "t": "Hoteles P80 analizados", "d": "Universo RND W22."}], "hotels": [["Hotel A NoDispo", "#FCE4F1", "#99162B", "Cr\u00edtica", "150k", "45,2%", "$210", false, "\u25bc5pp"], ["Hotel B NoDispo", "#FCE4F1", "#99162B", "Cr\u00edtica", "120k", "38,7%", "$180", false, "\u25bc3pp"], ["Hotel C NoDispo", "#FED7AA", "#C2410C", "Revisar", "90k", "18,3%", "$450", true, "\u25b21pp"], ["Hotel D NoDispo", "#FED7AA", "#C2410C", "Revisar", "80k", "12,1%", "$580", null, "\u2014"], ["Hotel E NoDispo", "#FEF9C3", "#713F12", "Aceptable", "70k", "4,8%", "$720", true, "\u25b22pp"]], "dims": [["Canc\u00fan", "#FCE4F1", "#99162B", "Cr\u00edtica", "2.1M", "28,4%", "$312", false, "\u25bc4pp"], ["Los Cabos", "#FED7AA", "#C2410C", "Revisar", "1.8M", "14,2%", "$520", null, "\u2014"], ["Riviera Maya", "#FEF9C3", "#713F12", "Aceptable", "1.5M", "5,1%", "$680", true, "\u25b21pp"], ["Puerto Vallarta", "#E1F5EE", "#1A6B4A", "Exitosa", "900k", "2,3%", "$890", true, "\u25b23pp"], ["Huatulco", "#E1F5EE", "#1A6B4A", "Exitosa", "400k", "1,8%", "$1.200", true, "\u25b22pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Apertura de cupos Canc\u00fan \u2014 hoteles con NoDispo > 30%.", "t": "NoDispo", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Revisar paridad B2C \u2014 mayor NoDispo del canal.", "t": "Paridad", "p": "W22"}], "co": ["Canc\u00fan NoDispo \u00b7 escalamiento W21 \u00b7 en seguimiento"]}, "b2c": {"re": [{"n": "3,31%", "t": "NoDispo B2C \u00b7 <b class=\"sev-badge\" style=\"background:#FED7AA;color:#C2410C;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Revisar</b>", "d": "Mayor NoDispo de los 3 canales."}, {"n": "$248", "t": "IPM B2C \u00b7 <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "Muy por debajo del target $650."}, {"n": "200", "t": "Hoteles B2C <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+ NoDispo</b>", "d": "Alta demanda perdida."}, {"n": "90", "t": "Hoteles B2C <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "Sin booking B2C."}, {"n": "50", "t": "Hoteles B2C IPM <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "IPM < $200."}, {"n": "52%", "t": "Hotel X \u00b7 peor NoDispo B2C", "d": "Demanda perdida cr\u00edtica."}, {"n": "18k", "t": "Hotel X \u00b7 mayor tr\u00e1fico B2C", "d": "NoDispo 52%."}, {"n": "$80", "t": "Hotel Y \u00b7 peor IPM B2C", "d": "Revenue m\u00ednimo."}, {"n": "Canc\u00fan", "t": "Destino B2C peor NoDispo", "d": "Primera prioridad."}, {"n": "312", "t": "Hoteles P80 B2C", "d": "W22."}], "hotels": [["Hotel B2C 1", "#FCE4F1", "#99162B", "Cr\u00edtica", "80k", "52%", "$80", false, "\u25bc8pp"], ["Hotel B2C 2", "#FCE4F1", "#99162B", "Cr\u00edtica", "60k", "41%", "$120", false, "\u25bc5pp"], ["Hotel B2C 3", "#FED7AA", "#C2410C", "Revisar", "40k", "15%", "$320", true, "\u25b22pp"], ["Hotel B2C 4", "#FED7AA", "#C2410C", "Revisar", "30k", "9%", "$480", null, "\u2014"], ["Hotel B2C 5", "#FEF9C3", "#713F12", "Aceptable", "20k", "4%", "$680", true, "\u25b21pp"]], "dims": [["Canc\u00fan B2C", "#FCE4F1", "#99162B", "Cr\u00edtica", "800k", "38%", "$150", false, "\u25bc6pp"], ["Los Cabos B2C", "#FED7AA", "#C2410C", "Revisar", "600k", "19%", "$380", null, "\u2014"], ["Riviera Maya B2C", "#FEF9C3", "#713F12", "Aceptable", "500k", "6%", "$580", true, "\u25b22pp"], ["PV B2C", "#E1F5EE", "#1A6B4A", "Exitosa", "200k", "2%", "$820", true, "\u25b23pp"], ["Huatulco B2C", "#E1F5EE", "#1A6B4A", "Exitosa", "100k", "1%", "$980", true, "\u25b21pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Apertura cupos B2C Canc\u00fan \u2014 NoDispo 38%.", "t": "NoDispo", "p": "W22"}], "co": ["B2C NoDispo \u00b7 paridad en revisi\u00f3n"]}, "op": {"re": [{"n": "2,24%", "t": "NoDispo B2B-OP \u00b7 <b class=\"sev-badge\" style=\"background:#E1F5EE;color:#1A6B4A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Exitosa</b>", "d": "Mejor NoDispo de los 3 canales."}, {"n": "$688", "t": "IPM B2B-OP \u00b7 <b class=\"sev-badge\" style=\"background:#FEF9C3;color:#713F12;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Aceptable</b>", "d": "Sobre el target $650."}, {"n": "80", "t": "Hoteles OP <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+ NoDispo</b>", "d": "28%."}, {"n": "50", "t": "Hoteles OP <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "16%."}, {"n": "30", "t": "Hoteles OP IPM <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "IPM < $200."}, {"n": "35%", "t": "Hotel OP peor NoDispo", "d": "Canal opaco con menor NoDispo global."}, {"n": "25k", "t": "Hotel OP mayor tr\u00e1fico", "d": "NoDispo 35%."}, {"n": "$150", "t": "Hotel OP peor IPM", "d": "Revenue bajo en opaco."}, {"n": "Canc\u00fan", "t": "Destino OP peor NoDispo", "d": "Primera prioridad."}, {"n": "628", "t": "Hoteles P80 B2B-OP", "d": "W22."}], "hotels": [["Hotel OP 1", "#FCE4F1", "#99162B", "Cr\u00edtica", "60k", "35%", "$150", false, "\u25bc5pp"], ["Hotel OP 2", "#FCE4F1", "#99162B", "Cr\u00edtica", "45k", "28%", "$210", false, "\u25bc3pp"], ["Hotel OP 3", "#FED7AA", "#C2410C", "Revisar", "35k", "12%", "$420", true, "\u25b21pp"], ["Hotel OP 4", "#FED7AA", "#C2410C", "Revisar", "25k", "7%", "$560", null, "\u2014"], ["Hotel OP 5", "#FEF9C3", "#713F12", "Aceptable", "18k", "3%", "$740", true, "\u25b22pp"]], "dims": [["Canc\u00fan OP", "#FCE4F1", "#99162B", "Cr\u00edtica", "600k", "25%", "$280", false, "\u25bc4pp"], ["Los Cabos OP", "#FED7AA", "#C2410C", "Revisar", "500k", "12%", "$490", null, "\u2014"], ["Riviera Maya OP", "#FEF9C3", "#713F12", "Aceptable", "400k", "4%", "$700", true, "\u25b21pp"], ["PV OP", "#E1F5EE", "#1A6B4A", "Exitosa", "150k", "2%", "$950", true, "\u25b22pp"], ["Huatulco OP", "#E1F5EE", "#1A6B4A", "Exitosa", "80k", "1%", "$1.100", true, "\u25b21pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Apertura cupos OP Canc\u00fan \u2014 NoDispo 25%.", "t": "NoDispo", "p": "W22"}, {"c": "qw", "o": "ext.marco.ali", "a": "Revisar paridad OP \u2014 hoteles IPM Cr\u00edtica.", "t": "Paridad", "p": "W22"}], "co": ["OP NoDispo \u00b7 W21 \u00b7 en seguimiento"]}, "cug": {"re": [{"n": "2,82%", "t": "NoDispo CUG \u00b7 <b class=\"sev-badge\" style=\"background:#E1F5EE;color:#1A6B4A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Exitosa</b>", "d": "Canal privado lidera NoDispo."}, {"n": "$787", "t": "IPM CUG \u00b7 <b class=\"sev-badge\" style=\"background:#FEF9C3;color:#713F12;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Aceptable</b>", "d": "Segundo mejor IPM."}, {"n": "60", "t": "Hoteles CUG <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica+ NoDispo</b>", "d": "32%."}, {"n": "30", "t": "Hoteles CUG <b class=\"sev-badge\" style=\"background:#F2EEE6;color:#5F5E5A;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Sin Conv</b>", "d": "10%."}, {"n": "20", "t": "Hoteles CUG IPM <b class=\"sev-badge\" style=\"background:#FCE4F1;color:#99162B;font-size:8px;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);\">Cr\u00edtica</b>", "d": "IPM < $200."}, {"n": "42%", "t": "Hotel CUG peor NoDispo", "d": "Luxury con alta demanda no atendida."}, {"n": "15k", "t": "Hotel CUG mayor tr\u00e1fico", "d": "NoDispo 42%."}, {"n": "$180", "t": "Hotel CUG peor IPM", "d": "Revenue bajo en canal privado."}, {"n": "Canc\u00fan", "t": "Destino CUG peor NoDispo", "d": "Primera prioridad."}, {"n": "184", "t": "Hoteles P80 CUG", "d": "W22."}], "hotels": [["Hotel CUG 1", "#FCE4F1", "#99162B", "Cr\u00edtica", "40k", "42%", "$180", false, "\u25bc6pp"], ["Hotel CUG 2", "#FCE4F1", "#99162B", "Cr\u00edtica", "30k", "33%", "$250", false, "\u25bc4pp"], ["Hotel CUG 3", "#FED7AA", "#C2410C", "Revisar", "22k", "14%", "$480", true, "\u25b21pp"], ["Hotel CUG 4", "#FED7AA", "#C2410C", "Revisar", "18k", "8%", "$620", null, "\u2014"], ["Hotel CUG 5", "#FEF9C3", "#713F12", "Aceptable", "12k", "3%", "$850", true, "\u25b22pp"]], "dims": [["Canc\u00fan CUG", "#FCE4F1", "#99162B", "Cr\u00edtica", "400k", "32%", "$280", false, "\u25bc5pp"], ["Los Cabos CUG", "#FED7AA", "#C2410C", "Revisar", "300k", "16%", "$510", null, "\u2014"], ["Riviera Maya CUG", "#FEF9C3", "#713F12", "Aceptable", "250k", "5%", "$720", true, "\u25b21pp"], ["PV CUG", "#E1F5EE", "#1A6B4A", "Exitosa", "100k", "2%", "$980", true, "\u25b22pp"], ["Huatulco CUG", "#E1F5EE", "#1A6B4A", "Exitosa", "60k", "1%", "$1.300", true, "\u25b21pp"]], "plan": [{"c": "", "o": "hugo.ascencio", "a": "Apertura cupos CUG luxury \u2014 NoDispo 32%.", "t": "NoDispo", "p": "W22"}], "co": ["CUG NoDispo \u00b7 luxury chains \u00b7 en seguimiento"]}};
var CR_AL={"global": [["&#127968;", "Hoteles", "Marriott Canc\u00fan Resort", "72,1%", "Hyatt Ziva Los Cabos", "0,8%"], ["\ud83d\udccd", "Destinos", "Canc\u00fan", "78,3%", "Los Cabos", "0,9%"], ["\ud83c\udfe2", "Corporativo", "IHG Hotels & Resorts", "71,3%", "Hilton Worldwide", "1,2%"]], "b2c": [["&#127968;", "Hoteles", "Riu Palace Canc\u00fan", "68,4%", "Iberostar Para\u00edso", "0,7%"], ["\ud83d\udccd", "Destinos", "Canc\u00fan", "70,1%", "Los Cabos", "0,8%"], ["\ud83c\udfe2", "Corporativo", "RIU Hotels", "69,5%", "Palace Resorts", "1,0%"]], "op": [["&#127968;", "Hoteles", "Westin Canc\u00fan", "65,3%", "Dreams Riviera", "1,2%"], ["\ud83d\udccd", "Destinos", "Canc\u00fan", "66,1%", "Los Cabos", "1,1%"], ["\ud83c\udfe2", "Corporativo", "Marriott Intl", "66,1%", "Meli\u00e1 Hotels", "1,5%"]], "cug": [["&#127968;", "Hoteles", "Ritz-Carlton Canc\u00fan", "88,4%", "Belmond Maroma", "1,8%"], ["\ud83d\udccd", "Destinos", "Canc\u00fan", "89,0%", "Los Cabos", "2,0%"], ["\ud83c\udfe2", "Corporativo", "Marriott Luxury", "88,9%", "Belmond", "1,9%"]]};
var RND_AL={"global": [["&#127968;", "Hoteles", "Hotel A (45% NoDispo)", "45,2%", "Hotel B (IPM)", "$80"], ["\ud83d\udccd", "Destinos", "Canc\u00fan (28% NoDispo)", "28,4%", "Los Cabos (IPM)", "$312"], ["\ud83c\udfe2", "Corporativo", "Chain X NoDispo", "32%", "Chain Y IPM", "$150"]], "b2c": [["&#127968;", "Hoteles", "Hotel B2C 1", "52%", "Hotel B2C 2 (IPM)", "$80"], ["\ud83d\udccd", "Destinos", "Canc\u00fan B2C", "38%", "Los Cabos B2C", "$150"], ["\ud83c\udfe2", "Corporativo", "Corp B2C 1", "35%", "Corp B2C 2", "$180"]], "op": [["&#127968;", "Hoteles", "Hotel OP 1", "35%", "Hotel OP 2 (IPM)", "$150"], ["\ud83d\udccd", "Destinos", "Canc\u00fan OP", "25%", "Los Cabos OP", "$280"], ["\ud83c\udfe2", "Corporativo", "Corp OP 1", "28%", "Corp OP 2", "$210"]], "cug": [["&#127968;", "Hoteles", "Hotel CUG 1", "42%", "Hotel CUG 2 (IPM)", "$180"], ["\ud83d\udccd", "Destinos", "Canc\u00fan CUG", "32%", "Los Cabos CUG", "$280"], ["\ud83c\udfe2", "Corporativo", "Corp CUG 1", "36%", "Corp CUG 2", "$250"]]};

function g(id){return document.getElementById(id);}
function cv(){return W.mode==='cr'?CR_CV[W.canasta]:RND_CV[W.canasta];}
function data(){return W.mode==='cr'?CR_D[W.canasta]:RND_D[W.canasta];}
function al(){return W.mode==='cr'?CR_AL[W.canasta]:RND_AL[W.canasta];}

function trow(r){
 var wb=r[7]===null?'#F2EEE6':(r[7]?'#EAF3DE':'#FCE8E6');
 var wf=r[7]===null?'#8A8377':(r[7]?'#2F6C34':'#C0392B');
 return '<tr style="border-bottom:1px solid var(--rule-soft);">'
  +'<td style="padding:9px 0 9px 12px;font-size:12px;font-weight:600;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="'+r[0]+'">'+r[0]+'</td>'
  +'<td style="padding:9px 8px;text-align:center;"><span class="sev-badge" style="background:'+r[1]+';color:'+r[2]+';font-size:7px;font-weight:700;padding:2px 6px;text-transform:uppercase;outline:1px solid rgba(0,0,0,.12);white-space:nowrap;">'+r[3]+'</span></td>'
  +'<td style="padding:9px 8px;text-align:right;font-size:12px;color:var(--ink-soft);">'+r[4]+'</td>'
  +'<td style="padding:9px 8px;text-align:right;font-size:12px;color:var(--ink-soft);">'+r[5]+'</td>'
  +'<td style="padding:9px 8px;text-align:right;font-size:12px;color:var(--ink-soft);">'+r[6]+'</td>'
  +'<td style="padding:9px 8px;text-align:right;"><em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 5px;border-radius:3px;background:'+wb+';color:'+wf+';white-space:nowrap;margin-right:4px;">'+r[8]+'</em><em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 5px;border-radius:3px;background:#F0F0F0;color:#666;white-space:nowrap;">'+r[9]+'</em></td>'
  +'<td style="padding:9px 12px 9px 8px;text-align:right;"><em style="font-style:normal;display:inline-block;font-size:8px;font-weight:700;padding:1px 5px;border-radius:3px;background:#EBF5F7;color:#0369A1;white-space:nowrap;">'+r[10]+'</em></td>'
  +'</tr>';
}

function w22_renderTable(tbodyId, btnId, rows, open){
 var tbody=g(tbodyId);if(!tbody)return;
 var PAGE=5,total=rows.length;
 tbody.innerHTML=rows.map(function(r,i){
  var hide=(i>=PAGE&&!open)?' style="display:none;"':'';
  return '<tr'+hide+' style="border-bottom:1px solid var(--rule-soft);">'
   +trow(r).replace('<tr style="border-bottom:1px solid var(--rule-soft);">','');
 }).join('');
 var btn=g(btnId);
 if(!btn)return;
 var remaining=total-PAGE;
 if(total<=PAGE){btn.style.display='none';return;}
 btn.style.display='';
 btn.textContent=open?'Ver menos ↑':'Ver '+remaining+' más ↓';
 btn.onclick=function(){
  /* toggle */
  var nowOpen=btn.textContent.indexOf('menos')>-1;
  w22_renderTable(tbodyId,btnId,rows,!nowOpen);
 };
}
function w22_renderRE(open){
 W.reOpen=open;
 var d=data(), col=cv().col;
 var el=g('w22-re-list');if(!el)return;
 el.innerHTML=d.re.map(function(r,i){
  var h=(i>=5&&!W.reOpen)?' style="display:none;"':'';
  return '<li'+h+' style="position:relative;padding:16px 0 16px 80px;border-bottom:1px solid var(--rule);font-size:15px;line-height:1.55;">'
   +'<span style="font-size:12px;color:var(--ink-muted);font-weight:500;position:absolute;left:0;top:20px;">'+(i<9?'0'+(i+1):i+1)+'</span>'
   +'<strong style="display:block;font-size:22px;font-weight:700;color:'+col+';letter-spacing:-.02em;margin-bottom:4px;">'+r.n+'</strong>'
   +'<span style="font-weight:600;color:var(--ink);">'+r.t+'</span> '
   +'<span style="color:var(--ink-muted);font-size:14px;">'+r.d+'</span></li>';
 }).join('');
 var btn=g('w22-re-btn');if(btn)btn.textContent=W.reOpen?'Ver menos ↑':'Ver 5 más ↓';
}
function w22_toggleRE(){w22_renderRE(!W.reOpen);}

function w22_renderAlertas(){
 var rows=al()||[];
 if(!Array.isArray(rows))rows=[];
 var el=g('w22-alertas');if(!el)return;
 var ef_lbl=W.mode==='cr'?'Peor Eficacia':'Mayor NoDispo';
 var cv_lbl=W.mode==='cr'?'Peor ConvRate':'Menor IPM';
 el.innerHTML=rows.map(function(r){
  return '<div style="border:1px solid var(--rule);padding:14px;background:var(--paper);">'
   +'<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--accent);margin-bottom:12px;">'+r[0]+' '+r[1]+'</div>'
   +'<div style="background:var(--paper-soft);border:1px solid var(--rule);padding:10px 12px;margin-bottom:8px;border-left:3px solid #EA0074;">'
   +'<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);margin-bottom:3px;">'+ef_lbl+'</div>'
   +'<div style="font-size:11px;font-weight:600;color:var(--ink);">'+r[2]+'</div>'
   +'<div style="font-size:13px;font-weight:700;color:#EA0074;margin-top:2px;">'+r[3]+'</div></div>'
   +'<div style="background:var(--paper-soft);border:1px solid var(--rule);padding:10px 12px;border-left:3px solid var(--accent);">'
   +'<div style="font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:.10em;color:var(--ink-muted);margin-bottom:3px;">'+cv_lbl+'</div>'
   +'<div style="font-size:11px;font-weight:600;color:var(--ink);">'+r[4]+'</div>'
   +'<div style="font-size:13px;font-weight:700;color:var(--accent);margin-top:2px;">'+r[5]+'</div></div></div>';
 }).join('');
}

function w22_update(){
 var c=cv(), col=c.col, d=data();

 /* Strip */
 var s1=g('w22-strip-ef');if(s1){s1.textContent=c.ef;s1.style.color=col;}
 var s2=g('w22-strip-cv');if(s2){s2.textContent=c.cv;s2.style.color=col;}
 var sb=g('w22-strip-band');if(sb){sb.style.background=c.bbg;sb.style.color=c.bfg;sb.textContent=c.band;}
 /* Labels del strip según modo */
 var l1=g('w22-strip-lbl1'),l2=g('w22-strip-lbl2');
 if(W.mode==='cr'){if(l1)l1.textContent='Eficacia';if(l2)l2.textContent='Conv Rate';}
 else{if(l1)l1.textContent='NoDispo';if(l2)l2.textContent='IPM';}

 /* KPI cards W21 */
 var kef=g('w21-kv-ef');if(kef){kef.textContent=c.ef;kef.style.color=col;}
 var kcv=g('w21-kv-cv');if(kcv){kcv.textContent=c.cv;kcv.style.color=col;}
 var hef=g('w21-hist-ef');if(hef)hef.style.color=col;
 var hcv=g('w21-hist-cv');if(hcv)hcv.style.color=col;

 /* Chips */
 document.querySelectorAll('.c-chip').forEach(function(el){
  var a=el.classList.contains('active');
  el.style.borderBottomColor=a?col:'transparent';
  el.style.color=a?col:'';el.style.background=a?'var(--paper)':'';
 });

 /* Tablas */
 w22_renderTable('w22-th','w22-th-more',d.hotels,false);
 /* Renderizar dimensión activa (por defecto corp) */
 var dim_key = W.dim || 'corp';
 var dim_data = d[dim_key+'s'] || d.dims || [];
 w22_renderTable('w22-td','w22-td-more',dim_data,false);

 /* RE + Alertas + Plan */
 w22_renderRE(false);
 w22_renderAlertas();

 var pg=g('w22-pg');
 if(pg)pg.innerHTML=d.plan.map(function(p){
  var bc=p.c==='qw'?'#2F6C34':p.c==='mp'?'#A86A1D':'var(--accent)';
  var bgc=p.c==='qw'?'#E0F0E2':p.c==='mp'?'#FFF4E0':'var(--accent-soft)';
  return '<div style="background:var(--paper);border:1px solid var(--rule);border-left:3px solid '+bc+';padding:10px 14px;border-radius:3px;">'
   +'<div style="display:inline-block;font-size:9px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:'+bc+';background:'+bgc+';padding:3px 8px;border-radius:2px;margin-bottom:6px;">'+p.o+'</div>'
   +'<div style="font-size:12px;line-height:1.4;color:var(--ink-soft);">'+p.a+'</div>'
   +'<div style="display:flex;gap:10px;margin-top:7px;font-size:10px;color:var(--ink-muted);">'
   +'<span style="font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-soft);background:var(--paper-soft);padding:2px 7px;border-radius:2px;font-size:9px;">'+p.t+'</span>'
   +'<span><strong style="font-size:8px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft);margin-right:3px;">Plazo</strong>'+p.p+'</span></div></div>';
 }).join('');

 var co=g('w22-co');
 if(co)co.innerHTML=d.co.map(function(c,i){
  return '<div style="font-size:12px;color:var(--ink-soft);padding:6px 0;border-bottom:1px solid var(--rule-soft);display:flex;gap:10px;">'
   +'<span style="font-size:10px;font-weight:700;color:var(--ink-muted);min-width:18px;">'+(i+1)+'.</span><span>'+c+'</span></div>';
 }).join('');

 /* Canvas */
 w22_redrawCanvas(col);
 w22_recolorSparks(col);
}

function w22_setMode(m, el){
 W.mode=m; W.canasta='global'; W.reOpen=false;
 /* Segmented control — colores dinámicos según modo */
 var modeCol=m==='cr'?'#5C469C':'#EA0074';
 var seg=document.querySelector('.w22-seg');
 if(seg){seg.style.border='1.5px solid '+modeCol;seg.style.borderRadius='4px';}
 var btns=document.querySelectorAll('.w22-seg-btn');
 btns.forEach(function(c,i){
  c.classList.remove('on');
  c.style.background='';c.style.color='';
  if(i===0)c.style.borderRight='1.5px solid '+modeCol;
 });
 el.classList.add('on');
 el.style.background=modeCol;el.style.color='#fff';
 /* Masthead report-tag */
 var tag=document.getElementById('w22-report-tag');
 if(tag){tag.textContent=m==='cr'?'CheckRates':'RatesNoDispo';tag.style.background=modeCol;}
 /* Mostrar/ocultar bloques KPI */
 var cr_block=g('kpis-hero-section');
 var rnd_block=g('w22-rnd-block');
 if(cr_block)cr_block.style.display=m==='cr'?'':'none';
 if(rnd_block)rnd_block.style.display=m==='rnd'?'':'none';
 /* Reset canasta chips */
 document.querySelectorAll('.c-chip').forEach(function(x){
  x.classList.remove('active');x.style.borderBottomColor='transparent';x.style.color='';x.style.background='';
 });
 var gc=g('chip-global');if(gc)gc.classList.add('active');
 w22_update();
}

function w22_setC(c,el){
 W.canasta=c; W.reOpen=false;
 document.querySelectorAll('.c-chip').forEach(function(x){
  x.classList.remove('active');x.style.borderBottomColor='transparent';x.style.color='';x.style.background='';
 });
 el.classList.add('active');
 w22_update();
}
function w22_setView(v){
 W.view=v;
 var ph=g('w22-ph'),pd=g('w22-pd'),vh=g('vch-h'),vd=g('vch-d');
 if(ph)ph.style.display=v==='hotel'?'block':'none';
 if(pd)pd.style.display=v==='dim'?'block':'none';
 if(vh){vh.classList.toggle('on',v==='hotel');vh.style.background=v==='hotel'?'var(--paper)':'';vh.style.color=v==='hotel'?'var(--ink)':'var(--ink-muted)';}
 if(vd){vd.classList.toggle('on',v==='dim');vd.style.background=v==='dim'?'var(--paper)':'';vd.style.color=v==='dim'?'var(--ink)':'var(--ink-muted)';}
}
function w22_setDim(d){
 W.dim = d;
 var l={corp:'Corporativo',dest:'Destino',chan:'Channel'};
 var th=g('w22-th-dim');if(th)th.textContent=l[d]||'Corporativo';
 w22_update();
}
function w22_iTab(el){
 var row=el.parentElement;
 row.querySelectorAll('label').forEach(function(t){
  t.classList.remove('active');
  t.style.background='';t.style.color='';t.style.border='';t.style.borderBottom='';t.style.marginBottom='';
 });
 el.classList.add('active');
 el.style.background='var(--paper)';el.style.color='var(--accent)';
 el.style.border='1px solid var(--rule)';el.style.borderBottom='1px solid var(--paper)';
 el.style.marginBottom='-1px';
}

/* Recolorear spark bars del histórico W21 */
function w22_recolorSparks(accent){
 var rgb={'#333132':'51,49,50','#EA0074':'234,0,116','#FCB000':'252,176,0','#4FC3F4':'79,195,244','#1A6B4A':'26,107,74'};
 var accentRgb=rgb[accent]||'92,70,156';
 ['hist-hcr-global-ef-spark','hist-hcr-global-cv-spark'].forEach(function(sid){
  var el=g(sid);if(!el)return;
  var bars=el.querySelectorAll('div');
  var n=bars.length;
  bars.forEach(function(bar,i){
   var isLast=(i===n-1);
   /* Recalcular alpha proporcional — last=accent sólido, resto proporcional */
   if(isLast){bar.style.background=accent;}
   else{
    /* Mantener el alpha relativo original — lo extraemos del title para calcular la altura */
    var h=parseInt(bar.style.height)||8;
    var alpha=Math.round((0.25+0.70*(h-4)/14)*100)/100;
    bar.style.background='rgba('+accentRgb+','+alpha+')';
   }
  });
 });
}
/* Canvas */
var HIST_CR={'hcr-global-ef':{vals:[93.58,93.71,93.3,93.34,93.15],target:97.0},'hcr-global-cv':{vals:[1.15,1.02,1.14,1.63,1.57],target:2.5}};
var RGB={'#333132':'51,49,50','#EA0074':'234,0,116','#FCB000':'252,176,0','#4FC3F4':'79,195,244','#1A6B4A':'26,107,74'};
/* Tooltip state */
var W22_CANVAS_PTS={};
var W22_CANVAS_CFG={};
var W22_TOOLTIP=null;
function w22_getTooltip(){
 if(!W22_TOOLTIP){
  var t=document.createElement('div');
  t.id='w22-canvas-tip';
  t.style.cssText='position:fixed;pointer-events:none;display:none;background:var(--ink);color:#fff;font-size:10px;font-weight:700;padding:4px 8px;border-radius:3px;z-index:9999;white-space:nowrap;letter-spacing:.02em;';
  document.body.appendChild(t);
  W22_TOOLTIP=t;
 }
 return W22_TOOLTIP;
}
function w22_bindCanvasTip(el,cid,cfg,pts){
 W22_CANVAS_PTS[cid]=pts;
 W22_CANVAS_CFG[cid]=cfg;
 el.onmousemove=function(e){
  /* Usar siempre W22_CANVAS_CFG/PTS actuales — permiten actualización tras click */
  var liveCfg=W22_CANVAS_CFG[cid]||cfg;
  var rect=el.getBoundingClientRect();
  var mx=e.clientX-rect.left;
  var tip=w22_getTooltip();
  /* Recalcular pts con ancho real del canvas */
  var w=rect.width||el.offsetWidth||400;
  var vals=liveCfg.vals;
  var livePts=vals.map(function(v,i){return{x:(i/(vals.length-1))*w};});
  var best=-1,bestDx=9999;
  livePts.forEach(function(p,i){var dx=Math.abs(p.x-mx);if(dx<bestDx){bestDx=dx;best=i;}});
  if(best<0||bestDx>40){tip.style.display='none';return;}
  var sem=liveCfg.semanas?liveCfg.semanas[best]:('W'+(17+best));
  var val=vals[best];
  var fmtVal=liveCfg.metric==='ipm'?('$'+val.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g,',')):val.toFixed(2)+'%';
  tip.textContent=sem+': '+fmtVal;
  tip.style.display='block';
  tip.style.left=(e.clientX+10)+'px';
  tip.style.top=(e.clientY-28)+'px';
 };
 el.onmouseleave=function(){
  var tip=w22_getTooltip();tip.style.display='none';
 };
}
function w22_redrawCanvas(accent){
 var rgb=RGB[accent]||'92,70,156';
 var hist=W.mode==='cr'?HIST_CR:{};
 Object.keys(hist).forEach(function(cid){
  var cfg=hist[cid],el=g(cid);if(!el||!el.getContext)return;
  el.width=el.offsetWidth||400;el.height=76;
  var ctx=el.getContext('2d'),vals=cfg.vals,h=el.height-10;
  var mn=Math.min.apply(null,vals),mx=Math.max.apply(null,vals),dR=mx-mn+0.0001;
  var pts=vals.map(function(v,i){return{x:(i/(vals.length-1))*el.width,y:el.height-((v-mn)/dR*h+5)};});
  var tY=el.height-((cfg.target-mn)/dR*h+5);
  ctx.clearRect(0,0,el.width,el.height);
  ctx.strokeStyle='rgba(0,0,0,0.15)';ctx.lineWidth=1;ctx.setLineDash([3,2]);
  ctx.beginPath();ctx.moveTo(0,tY);ctx.lineTo(el.width,tY);ctx.stroke();ctx.setLineDash([]);
  ctx.beginPath();ctx.moveTo(pts[0].x,el.height);ctx.lineTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);
  ctx.lineTo(pts[pts.length-1].x,el.height);ctx.closePath();
  ctx.fillStyle='rgba('+rgb+',0.12)';ctx.fill();
  ctx.strokeStyle=accent;ctx.lineWidth=2;ctx.lineCap='round';ctx.lineJoin='round';
  ctx.beginPath();ctx.moveTo(pts[0].x,pts[0].y);
  for(var i=1;i<pts.length;i++)ctx.lineTo(pts[i].x,pts[i].y);ctx.stroke();
  for(var i=0;i<pts.length;i++){
   var last=i===pts.length-1;
   ctx.fillStyle=last?accent:'rgba('+rgb+',0.5)';ctx.globalAlpha=last?1:0.5;
   ctx.beginPath();ctx.arc(pts[i].x,pts[i].y,last?3:2,0,2*Math.PI);ctx.fill();ctx.globalAlpha=1;
  }
  /* Bind tooltip */
  var tipCfg={vals:cfg.vals,semanas:['W17','W18','W19','W20','W21'],metric:cid.indexOf('cv')>-1?'convrate':cid.indexOf('ipm')>-1?'ipm':cid.indexOf('nd')>-1?'nodispo':'eficacia'};
  w22_bindCanvasTip(el,cid,tipCfg,pts);
 });
}

w22_update();
[100,400,900].forEach(function(d){setTimeout(function(){var col=cv().col;w22_redrawCanvas(col);w22_recolorSparks(col);},d);});
window.addEventListener('resize',function(){setTimeout(function(){w22_redrawCanvas(cv().col);},100);});
/* Tooltip en canvas del IIFE W21 */
setTimeout(function(){
 Object.keys(HIST_CR).forEach(function(cid){
  var el=document.getElementById(cid);if(!el)return;
  var cfg=HIST_CR[cid];
  var tipCfg={vals:cfg.vals,semanas:['W17','W18','W19','W20','W21'],
   metric:cid.indexOf('cv')>-1?'convrate':'eficacia'};
  function rebind(){
   var w=el.offsetWidth||400,hh=76,lh=hh-10;
   var mn=Math.min.apply(null,cfg.vals),mx=Math.max.apply(null,cfg.vals),dR=mx-mn+0.0001;
   var pts=cfg.vals.map(function(v,i){return{x:(i/(cfg.vals.length-1))*w,y:hh-((v-mn)/dR*lh+5)};});
   w22_bindCanvasTip(el,cid,tipCfg,pts);
  }
  rebind();setTimeout(rebind,600);setTimeout(rebind,1400);
 });
},1000);
