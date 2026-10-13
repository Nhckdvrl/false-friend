"""Build six output-blind ZH sense/application cases; no model outputs read.

Run from repository root: python -m scripts.build_doppelganger_followup_v2
Ambiguous original/masked variants have null gold, not a benchmark-derived label.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from scripts.run_doppelganger_diagnostics import records,selected_families,SOURCE_SHA

root=Path(__file__).resolve().parents[1]
source=root/'data/raw/Doppelganger-JC'
assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==SOURCE_SHA
rs=records(source)
fs=selected_families(rs,24)
lookup={r['word_jp']:r for r in rs if r['task']=='context' and r['source_language']=='zh' and r['lexeme_family_id'] in fs}
rows=[]

def add(word,rev,target,original,paraphrase,question,options,original_gold,rationale,boundary,foil=None,slot_replacements=None,lexical_sources=None):
 r=lookup[word]
 if rev=='source_original':
  assert original is None
  original=r['sentence']
 assert original.count(target)==1
 assert target not in paraphrase and target not in question
 if foil is not None:
  assert target not in foil
 variants=['original','paraphrase','masked'] if foil is None else ['original','paraphrase','foil_paraphrase','masked']
 golds={'original':original_gold,'paraphrase':0,'masked':None}
 if foil is not None:
  golds['foil_paraphrase']=1
  assert slot_replacements is not None
  prefix,suffix=original.split(target)
  assert paraphrase==prefix+slot_replacements['paraphrase']+suffix
  assert foil==prefix+slot_replacements['foil_paraphrase']+suffix
 row={
  'schema_version':'doppelganger-downstream-v2','item_id':f"followup-v2:{r['lexeme_family_id']}:zh:{rev}",
  'lexeme_family_id':r['lexeme_family_id'],'source_language':'zh','word_jp':r['word_jp'],'word_zh':r['word_zh'],
  'target_word':target,'context_revision':rev,'source_context':r['sentence'],
  'context_original':original,'context_paraphrase':paraphrase,'context_masked':original.replace(target,'［词语］'),
  'question':question,'options':options,'correct_index':original_gold,'variant_correct_indices':golds,
  'variants':variants,'option_orders':[[0,1],[1,0]],
  'original_gold_status':'context_supports_local_reading' if original_gold is not None else 'ambiguous_or_nonexclusive_no_unique_gold',
  'task_kind':'sense_conditioned_application','hypothesis_role':'explicit_meaning_pair_responsiveness_and_lexeme_tendency',
  'source_intended_sense_reference_index':0,
  'paraphrase_relation':'Explicit instantiation of one reading; not claimed equivalent to all readings of ambiguous original.',
  'review':{'reviewer_type':'two_research_agents_output_blind_not_human_or_native_speakers',
            'status':'TWO_AGENT_OUTPUT_BLIND_REVIEWED',
            'primary_reviewer':'/root/semantic_followup','secondary_reviewer':'/root/methods_review','independent_human_review':False,
            'secondary_review_scope':'No v1/v2 semantic-followup outputs read; secondary reviewer previously inspected baseline scores; minimal-pair naturalness, application gold, target/reference clarity, null gold, metadata chronology',
            'rationale':rationale,'contrast_boundary':boundary,
            'remaining_cue_risk':'Source context and question may select an answer without the target; mask has null gold and is scored as sense preference only.',
            'gold_strength':'locally_reviewed_explicit_sense_application_for_scored_variants'},
  'lexical_sources':lexical_sources or [],
  'provenance':{'source_repository':'https://github.com/0017-alt/Doppelganger-JC','source_sha':SOURCE_SHA,
     'source_context_item_id':r['item_id'],'selection':'preselected24_then_semantic_review_blind_to_model_outputs',
     'source_label_usage':'Reference only; null original gold where local sense is not identifiable.',
     'new_context':rev!='source_original','new_question':True,'new_paraphrase':True,
     'exploration_status':'V2 design after the v1 exploratory cycle; no v2 outputs viewed; not held out. Primary and secondary designers also did not inspect v1 outputs; root-level followup selection was not preregistered across cycles.'}}
 if foil is not None:
  row.update({'context_foil_paraphrase':foil,'slot_replacements':slot_replacements,
              'paired_variants':['paraphrase','foil_paraphrase'],'foil_changes_semantics':True,
              'foil_gold_flip':True})
 row['variant_prompts']={v:'请阅读下面的中文句子并回答问题。\n'+row['context_'+v]+'\n'+question for v in variants}
 rows.append(row)

sources_b=['https://dict.concised.moe.edu.tw/dictView.jsp?ID=1899&la=0&powerMode=0',
'https://www.rebe.ntpu.edu.tw/web/study/study_in.jsp?np_id=NP1736861666142']
b='现代中文同时有物件修理和补足课程两义。教育场景的補修不必是重修不及格课程；不能把中文物理修理读法叫作日语侵入。低线索原句不确定指哪一类，故不给gold。明确双义改写只检验对文本中指定意义的响应。'
q='按句中提到的事情，这项安排直接接入哪一种工作流程？'
o=['教务排课、课程学习和相应考核','勘查物件破损、准备材料和修复施工']
add('補修','source_original','補修',None,'這學期我有兩門課需要補行修讀。',q,o,0,
 '学期、两门课确定课程读法。改写只说补行修读，不添加已不及格或必然取得学分的断言；相应流程不要求一定课堂面授。',b,lexical_sources=sources_b)
add('補修','new_low_cue_v2','補修','他把補修的時間排在下週。','他把補上所缺課程的時間排在下週。',q,o,None,
 '安排时间本身不能区分课程与物件修理。两种显式替换都只动同一词槽，并保持自然句法、人物、时点和问题不变。',b,
 foil='他把修好破損物件的時間排在下週。',slot_replacements={'paraphrase':'補上所缺課程','foil_paraphrase':'修好破損物件'},lexical_sources=sources_b)

sources_d=['https://dict.revised.moe.edu.tw/dictView.jsp?ID=42405&q=1&word=%E6%80%A0']
b='待客不周与做事怠惰可能互为原因、在同一人身上共存；本题问明说的问题所对应的检查，不声称心理机制互斥。中文怠惰义有历史词典证据但不据此假定现代同等常用。原句客套读法自然，却不足以把一般事务疏忽绝对判错，故original不计准确率。'
q='只对照句中明确提到的问题，不推测它的隐藏原因，应优先检查哪项？'
o=['来访者有没有被及时招呼、礼貌回应','应办的事情有没有被懒散拖延、搁着不做']
add('怠慢','source_original','怠慢',None,'请多多包涵，待客失礼之处还请见谅。',q,o,None,
 '显式改写选择通常客套场景中的待客读法，而不冒充原句唯一真义。原句自身不新增客人，保持null gold。',b,lexical_sources=sources_d)
add('怠慢','new_low_cue_v2','怠慢','他担心怠慢会造成麻烦。','他担心待客失礼会造成麻烦。',q,o,None,
 '担心造成麻烦不能确定失误类别。两种替换都指向行为；不因现代某读法更频繁就给原词强制标签。',b,
 foil='他担心做事懒散拖延会造成麻烦。',slot_replacements={'paraphrase':'待客失礼','foil_paraphrase':'做事懒散拖延'},lexical_sources=sources_d)

sources_c=['https://dict.concised.moe.edu.tw/dictView.jsp?ID=13894&la=0&powerMode=0']
b='现代中文确有空调设备与冷空气两义，不能把冷空气选择视为日语侵入。房间热同时兼容无制冷设备与无冷空气；原source标签只是一个可行读法。显式二义题借助规定好的对象分类，属于简单语义应用，不是复杂因果推理。'
q='记录员按所指对象分组：设备组登记可制造、安装的机器；环境组记录空气本身的温度和流动。句中“没有”后提到的对象应归给哪一组？'
o=['设备组','环境组']
add('冷気','source_original','冷气',None,'这个房间没有空调设备，我觉得很热。',q,o,None,
 '原句没有冷气可指无设备或没有凉气，不以源标签强行排除另一义。改写明确设备读法，所以只有明确改写评分。',b,lexical_sources=sources_c)
q='记录员按所指对象分组：设备组登记可制造、安装的机器；环境组记录空气本身的温度和流动。句中“注意到”的对象应归给哪一组？'
add('冷気','new_low_cue_v2','冷气','她注意到这里的冷气。','她注意到这里的空调设备。',q,o,None,
 '注意到能自然支配设备和空气。两个显式意义保持完全相同的前后文，并通过限定的登记职责给出相反的分组答案。',b,
 foil='她注意到这里的冷空气。',slot_replacements={'paraphrase':'空调设备','foil_paraphrase':'冷空气'},lexical_sources=sources_c)

assert len(rows)==6 and len({r['lexeme_family_id'] for r in rows})==3
assert len({r['item_id'] for r in rows})==6
path=root/'data/processed/doppelganger_followup_v2.jsonl'
path.parent.mkdir(exist_ok=True,parents=True)
path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
print(json.dumps({'path':str(path),'items':len(rows),'families':3,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'trials_per_model':sum(2*len(r['variants']) for r in rows),
 'scored_variants_per_model':sum(sum(x is not None for x in r['variant_correct_indices'].values()) for r in rows),
 'paired_instances':3},indent=2))
