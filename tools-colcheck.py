# -*- coding: utf-8 -*-
import io, re, json
SCHEMA={
"audit":"id,at,actor,role,worker_id,action,entity,entity_id,label,before,after",
"breaks":"id,worker_id,started_at,ended_at",
"collections":"id,name,target_date,notes,status,created_at",
"design_projects":"id,name,images,notes,status,product_id,created_at,collection_id,stage,mood,sketches,materials,size_chart,sample_worker_id,sample_started_at,sample_finished_at,sample_notes,final_name,final_name_en,revisions,sku,checklist,patterns,sample_external,sample_vendor_id,sample_vendor,sample_cost,sample_currency,sample_due,sample_sent_at,refs,chart_unit",
"expenses":"id,trip_id,category,label,amount,currency,fx_rate,spent_on,note,created_at,collection_id",
"ext_jobs":"id,kind,vendor,status,line_ids,sent_at,expected_back,returned_at,notes,created_at,part_ids,is_fix,supplier_id,collection_id,order_id,trip_id,qty,unit_price,currency,fx_rate,delivery_date,pay_log,note_price,received_qty",
"line_parts":"id,line_id,part_ar,part_en,status,worker_id,started_at,finished_at,stage,emb_kind,emb_note,emb_artwork,emb_when,is_fix",
"materials":"id,sku,name,color,unit,supplier,price,active,created_at,supplier_id,design_id,consumption,kind,price_unit",
"order_lines":"id,order_id,product_id,size,color,qty,custom_specs,stage,stage_status,claimed_by,created_at,prep_note,fix_reason,fix_image,external_make,ext_fix_count",
"orders":"id,order_no,order_type,customer_ref,repair_reason,due_date,status,notes,created_at,repair_image,repair_note",
"photoshoots":"id,product_id,status,done_at,created_at",
"products":"id,name,name_en,images,patterns,components,embroidery,embroidery_kind,embroidery_note,artwork_url,external_make,size_chart,est_cut_min,est_sew_min,notes,active,created_at,sku,materials,est_parts,bom,garment_type,meas_rows,bom_parts,est_cut_parts,emb_parts,chart_image,chart_unit",
"purchases":"id,trip_id,channel,supplier_id,supplier_name,material_id,fabric_name,product_id,plan_qty,qty_yd,unit_price,currency,fx_rate,deposit,status,note,created_at,design_id,kind,unit,balance,paid,sample_id,buy_unit,buy_qty,plan_meters,deliver_status,ready_eta,pickup_place,pay_log,stage,order_id,collection_id,received_at,received_qty,qty_manual",
"repair_reasons":"id,label,active",
"settings":"id,work_start,work_end,work_days,break_minutes,creative_pin,updated_at,creative_tabs,channels,finance_locked",
"stage_events":"id,line_id,part_id,stage,worker_id,started_at,finished_at,result",
"stock_moves":"id,item_kind,material_id,product_id,size,color,qty,unit,reason,ref_table,ref_id,design_id,order_id,collection_id,note,actor,at",
"supplier_payments":"id,trip_id,channel,supplier_key,supplier_id,supplier_name,amount,currency,kind,paid_on,receipt,note,discrepancy_note,created_at,collection_id,stage,design_id,alloc",
"suppliers":"id,kind,name,shop_no,market,city,phone,wechat,notes,rating,created_at,plaza,floor,contact_person,channel,status,card_photos,address,wechat_qr,meas_unit",
"trip_samples":"id,trip_id,supplier_id,supplier_name,shop_no,photos,price,currency,per,fabric_type,width,note,product_id,design_id,status,created_at,checklist_item_id,card_photo,count,per_count,kind,channel,design_ids,card_photos,sku",
"trips":"id,name,start_date,end_date,status,notes,fx,expenses,created_at,channel,collection_ids",
"workers":"id,name,name_en,specialties,pin,active,created_at",
}
COLS={t:set(c.split(",")) for t,c in SCHEMA.items()}
src=io.open("index.html",encoding="utf-8").read()

def balanced(s, i):
    """i يشير لـ '{' — نرجّع محتواها"""
    d=0; st=i
    while i<len(s):
        ch=s[i]
        if ch in "{[(": d+=1
        elif ch in "}])":
            d-=1
            if d==0: return s[st+1:i], i
        elif ch in "\"'`":
            q=ch; i+=1
            while i<len(s) and s[i]!=q:
                if s[i]=="\\": i+=1
                i+=1
        i+=1
    return None, i

def topkeys(body):
    keys=[]; d=0; i=0; start=0; tern=0
    while i<len(body):
        ch=body[i]
        if ch in "{[(": d+=1
        elif ch in "}])": d-=1
        elif ch in "\"'`":
            q=ch; i+=1
            while i<len(body) and body[i]!=q:
                if body[i]=="\\": i+=1
                i+=1
        elif ch=="?" and d==0:
            tern+=1
        elif ch==":" and d==0:
            if tern>0: tern-=1
            else:
                seg=body[start:i].strip()
                m=re.search(r'([A-Za-z_][A-Za-z0-9_]*)\s*$', seg)
                if m: keys.append(m.group(1))
        elif ch=="," and d==0:
            start=i+1; tern=0
        i+=1
    return keys

bad=[]
for m in re.finditer(r'from\("([a-z_]+)"\)\s*\.\s*(insert|update|upsert)\s*\(\s*\{', src):
    tbl=m.group(1); op=m.group(2)
    if tbl not in COLS: continue
    bi=src.index("{", m.end()-1)
    body,_=balanced(src, bi)
    if body is None: continue
    for k in topkeys(body):
        if k not in COLS[tbl]:
            line=src[:bi].count("\n")+1
            bad.append((line, tbl, op, k))
print("checked calls with literal objects")
for b in sorted(set(bad)):
    print("  line %d  %s.%s  ->  عمود غير موجود: %s" % b)
if not bad: print("  ✓ ما في عمود غير موجود")
