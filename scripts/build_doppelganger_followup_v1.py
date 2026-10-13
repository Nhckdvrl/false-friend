import hashlib,json
from pathlib import Path
from scripts.run_doppelganger_diagnostics import records,selected_families,SOURCE_SHA
root=Path(__file__).resolve().parents[1]
rs=records(root/'data/raw/Doppelganger-JC')
fs=selected_families(rs,24)
lookup={(r['word_jp'],r['source_language']):r for r in rs if r['task']=='context' and r['lexeme_family_id'] in fs}
rows=[]
def add(word,lang,rev,original,paraphrase,question,options,gold,kind,role,rationale,risk,boundary,target=None):
 r=lookup[word,lang]; target=target or (r['word_jp'] if lang=='jp' else r['word_zh'])
 if rev=='source_original':
  assert original is None
  original=r['sentence']
 assert original.count(target)==1,(word,original,target)
 assert target not in paraphrase,(target,paraphrase)
 assert target not in question,(target,question)
 mask='［語句］' if lang=='jp' else '［词语］'
 row={'schema_version':'doppelganger-downstream-v1','item_id':f"followup-v1:{r['lexeme_family_id']}:{lang}:{rev}",
 'lexeme_family_id':r['lexeme_family_id'],'source_language':lang,'word_jp':r['word_jp'],'word_zh':r['word_zh'],'target_word':target,
 'context_revision':rev,'source_context':r['sentence'],'context_original':original,'context_paraphrase':paraphrase,
 'context_masked':original.replace(target,mask),'question':question,'options':options,'correct_index':gold,
 'task_kind':kind,'hypothesis_role':role,'variants':['original','paraphrase','masked'],'option_orders':[[0,1],[1,0]],
 'review':{'reviewer_type':'two_research_agents_output_blind_not_human_or_native_speakers','status':'TWO_AGENT_OUTPUT_BLIND_REVIEWED',
 'rationale':rationale,'remaining_cue_risk':risk,'contrast_boundary':boundary,'gold_strength':'usual_usage' if kind=='typical_scenario_reference' or word=='潔白' else 'semantic_relation_given_stated_reading', 'primary_reviewer':'/root/semantic_followup', 'secondary_reviewer':'/root/methods_review', 'secondary_review_scope':'Before outputs: answer leakage, paraphrase preservation, gold strength, complete target masking', 'independent_human_review':False},
 'provenance':{'source_repository':'https://github.com/0017-alt/Doppelganger-JC','source_sha':SOURCE_SHA,
 'source_context_item_id':r['item_id'],'selection':'preselected24_then_semantic_review_blind_to_model_outputs',
 'source_label_usage':'Published label used for provenance only; new question gold locally assigned.',
 'new_context':rev!='source_original','new_question':True,'new_paraphrase':True}}
 prefix='次の日本語の文を読んで、質問に答えてください。' if lang=='jp' else '请阅读下面的中文句子并回答问题。'
 row['variant_prompts']={v:prefix+'\n'+row['context_'+v]+'\n'+question for v in row['variants']}
 rows.append(row)

# These are content and case/reference questions, not full translations.
q='文中の品を、現代日本語の一般的な商品分類に沿って置くとすると、どちらの売り場が適切ですか？'
o=['ビスケットや飴を扱う売り場','採れたままのリンゴやミカンを扱う売り場']
b='現代の日常語を対象とする。古い果実用法、水菓子、果実を使った加工品には一般化しない。典型分類であり、論理必然や原因推論ではない。'
add('菓子','jp','source_original',None,'お茶の時間に、甘い物などの間食用に作られた食品を用意しました。',q,o,0,'typical_scenario_reference','high_context_reference','現代の日常的な食品分類ではビスケットや飴の売り場が適切。加工された間食という局所読みに改写。','お茶の時間が間食を強く示唆するが、果実も茶の時間に出せる。maskedで残存手掛かりを測る。',b)
add('菓子','jp','new_low_cue_v1','彼女は菓子を選んだ。','彼女は、甘い物などの間食用に作られた食品を選んだ。',q,o,0,'typical_scenario_reference','intended_word_dependent_reference','選んだという動詞だけでは菓子類と生果実を区別しない。問いは分類した品の指示対象を問う。','選択肢の具体性と既定の食品分類だけでgoldを推測する可能性は残る。',b)
q='文中の「彼」と、この作品との関係として述べられているのはどちらですか？'; o=['その作品を書いた人','その作品を借りた人']; b='中国語の動詞「著书」も執筆を表すので、作者役割だけでは両言語の誤義を区別できない。同根・品詞差の境界対照。'
add('著書','jp','source_original',None,'彼が書いた本は世界中で読まれている。',q,o,0,'participant_reference','shared_root_boundary_control','作品が読まれることと著者が誰かは別。所有を表す「彼の」だけでは作者とは限らず、語が作者関係を支持する。','読まれているので作品であることは分かる。作者という回答を所有格から推測できる可能性もある。',b)
add('著書','jp','new_low_cue_v1','彼は私に自分の著書を見せた。','彼は私に自分が書いた本を見せた。',q,o,0,'participant_reference','shared_root_boundary_control','自分の所持品を見せること自体では執筆者・借り手は決まらない。改写が保持するのは作者関係。','所有者を作者とみなす常識的近道をmaskedで測る。',b)
q='文中と同じ時点の人物について、「その事柄がどういうものか、まったく分かっていなかった」と報告されました。この追加報告は元の文と両立しますか？'; o=['両立する','両立しない']; b='知って理解しているという文脈内読みに対する整合性。全詳細を説明できる、解決できる、という強い能力は要求しない。中国語にも理解の用法があり、誤答を中国語意味への侵入と直結させない。'
add('認識','jp','source_original',None,'彼はその問題を正しく知り、理解している。',q,o,1,'proposition_consistency','semantic_negation_consistency','正しく把握しているという原句と、同じ事柄を全く分かっていないという追加命題は両立しない。','正しく、問題という語から知的課題を推測できる。',b)
add('認識','jp','new_low_cue_v1','担当者はその事情を認識していた。','担当者はその事情を知り、理解していた。',q,o,1,'proposition_consistency','intended_word_dependent_consistency','過去時点で事情を把握していたことを、同時点で全く分からなかったという否定と照合する。','担当者、事情は情報処理を示唆するが、知識を持つことまでは保証しない。',b)
q='この人物の性質について、「自分の利益のためなら、悪いと知りつつ人をだましても平気だ」という説明は、本文の評価と両立しますか？'; o=['両立する','両立しない']; b='心・人物の道徳的評価を固定。法的無罪の証明や行動予測とは異なる。中国語「洁白」にも比喩的な心の清さがあるため、言語間の完全排他的意味対とは扱わない。'
add('潔白','jp','source_original',None,'彼は不正をするような後ろ暗さのない心を持っている。',q,o,1,'proposition_consistency','moral_vs_color_boundary','原句は色ではなく心の正しさを評価する。意図的な利己的欺きに平気という性格記述と相容れない。','心が道徳的次元を示すが、評価の正負はターゲットなしには確定しない。',b)
add('潔白','jp','new_low_cue_v1','彼は潔白な人物だ。','彼は不正をするような後ろ暗さのない人物だ。',q,o,1,'proposition_consistency','intended_word_dependent_consistency','人物の道徳的性質という同じ局所読みに保持。「心」という追加の意味選択手掛かりを除いた新句。','人物の形容語なので道徳評価を推測できる。選択肢自体の極端な悪評価による否定偏向もあり得る。',b)
q='上司が計画を進めてよいと認めたものの、上司自身が何かを実行すると約束したわけではない場合、本文の条件は満たされていますか？'; o=['満たされている','まだ満たされていない']; b='許可・受け入れを必要条件とする文脈と、発話者自身の約束を分ける。語一般の全用法は分離しない。'
add('承諾','jp','source_original',None,'上司が計画を進めてよいと認めてから、計画を進めます。',q,o,0,'condition_application','permission_vs_promise','上司の許可があれば原句の条件は成立し、上司自身が何かを履行する約束は不要。','上司、計画、得てからは許可手続を示唆する。質問内の対比は語を削除しても常識で推測できる可能性がある。',b)
q='本人は「明日返事をする」と約束しましたが、公開への同意はまだ示していません。文の条件に従えば、今すぐ写真を公開できますか？'; o=['公開できる','まだ公開できない']
add('承諾','jp','new_low_cue_v1','本人の承諾がなければ、その写真は公開しません。','本人が公開してよいと認めなければ、その写真は公開しません。',q,o,1,'condition_application','permission_vs_promise','返事の約束だけでは公開の許可条件を満たさない。原sourceでは許可あり・約束なし、ここでは許可なし・約束ありという逆向きの予測。','写真公開についての一般的な同意規範がターゲットなしでも正解を支持し得る。maskで確認する。',b)
q='假设没有任何人请他明天来，他是主动保证会来的。这个补充情节是否与原话矛盾？'; o=['矛盾','不矛盾']; b='中文「承诺」可用于主动保证；不声称中文不能表示接受请求。仅检验“是否必须先有他人的请求”的非必然关系，不把中国语所有用法与日语全部分离。'
add('承諾','zh','source_original',None,'他保证明天一定会来。',q,o,1,'speech_act_compatibility','promise_without_prior_request','主动保证无需先有对方请求，所以补充情节与原句可相容。新gold不依赖源词典把所有用法排他化。','题目给出主动保证，常识兼容回答偏向很强；须看masked差值。',b,target='承諾')
q='如果此前我并未向他提出要求，而是他主动保证交资料，原句仍能成立吗？'; o=['能成立','不能成立']
add('承諾','zh','new_low_cue_v1','他承諾把那份资料交给我。','他保证把那份资料交给我。',q,o,0,'speech_act_compatibility','promise_without_prior_request','交付行为的主动保证可以在没有请求时成立；不新增是否最终履约的推断。','把资料交给我的论元结构没有直接要求先有请求；“相容”一般基线可能偏高。',b,target='承諾')
q='这项工作' # overwritten: all JP items use JP questions.
q='この行為の費用を記録する場合、通常どちらの請求書と対応させますか？'; o=['傷んだ箇所に使う材料や作業の代金','単位を取り直すための講義の受講料']; b='現代日本語の文字列「補修」を修繕と読む。再履修の解釈との典型イベント役割の区別。費用の発生自体を原句から断定しない。'
add('補修','jp','source_original',None,'古い家の壁の傷んだ部分を直した。',q,o,0,'typical_scenario_reference','high_context_event_reference','壁を直す行為を条件つきの請求書場面に写像する。原文から有料だったとは推論していない。','古い家の壁が物理修繕をほぼ決める。高語境の陽性対照で、語単独の寄与は主張しない。',b)
add('補修','jp','new_low_cue_v1','彼は補修の費用を支払った。','彼は傷んだ箇所を直すための費用を支払った。',q,o,0,'typical_scenario_reference','intended_word_dependent_event_reference','費用を支払っただけでは修繕代と受講料を区別しない。行為から支出の対象を対応させる。','選択肢の表現頻度や抽象度差による推測を排除していない。',b)
q='この器具を用途別に分類するとき、通常どちらに当たりますか？'; o=['茶を入れるための湯を沸かす容器','生薬を入れて薬液を煎じるための専用鍋']; b='現代の日常語としての通常の道具分類。語源は煎薬器具であり、現代のやかんで薬を煎じる物理的可能性も否定しない。「やかん」の漢字表記の希少性を含む語形アクセス診断。'
add('薬缶','jp','source_original',None,'彼は新しい湯沸かし用のやかんでお湯を沸かしている。',q,o,0,'typical_scenario_reference','high_context_instrument_reference','現代の辞書上の道具用法を湯沸かし容器に対応させる。源句はすでにお湯を沸かす行為を示す。','お湯を沸かしているが正解を強く示す。語を除いても容易であることを予測する。',b)
add('薬缶','jp','new_low_cue_v1','彼は薬缶を一つ買った。','彼は湯を沸かすためのやかんを一つ買った。',q,o,0,'typical_scenario_reference','intended_word_dependent_instrument_reference','買うという動詞はどちらの道具とも自然。問いは通常の使用分類であり、本来の漢字から漢方専用鍋と推測する競合が可能。','paraphraseはひらがな表記と機能説明を両方与えるので改善を純粋な意味選択機構とは呼べない。',b)
q='文中で一括して休みと述べられている学校の所在地として条件を満たすのはどちらですか？'; o=['大阪府の区域の内側','大阪府の区域の外側']; b='府の行政区域内という現代用法。単純な空間的指示であり、深い後果推論ではない。中文源句の古風な住居用法との頻度差が大きい。'
add('府内','jp','source_original',None,'大阪府の区域の内側にある学校は明日休みです。',q,o,0,'spatial_reference','high_context_spatial_reference','学校の集合を区域の内側に限定する空間的参照。原句の学校一般の休みが全称かどうかには依存しない。','大阪を残すmaskでも所在地をほぼ推測できる。',b)
q='この文で述べられた居住地が大阪府の境界より外にあるという説明は、この文と両立しますか？'; o=['両立する','両立しない']
add('府内','jp','new_low_cue_v1','ここでいう府は大阪府です。彼女は府内に住んでいます。','ここでいう府は大阪府です。彼女はその府の区域の内側に住んでいます。',q,o,1,'proposition_consistency','intended_word_dependent_spatial_consistency','府がどの区域を指すかを両条件で明示し、内側に住むことと境界の外に住所があることを同じ住所の命題として照合する。','行政区域の語と質問の対比による推測は残る。別荘など複数住所を想定せず、文中の居住地について問う。',b)
assert len(rows)==18
assert len({r['lexeme_family_id'] for r in rows})==8
assert len({r['item_id'] for r in rows})==len(rows)
p=root/'data/processed/doppelganger_followup_v1.jsonl'
p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
print(json.dumps({'path':str(p),'items':len(rows),'families':len({r['lexeme_family_id'] for r in rows}),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scored_trials_per_model':len(rows)*3*2},indent=2))
