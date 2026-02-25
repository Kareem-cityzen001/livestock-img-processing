import torch
import os
p='Models/livestock_disease_detection.pth'
if not os.path.exists(p):
    print('NO_CHECKPOINT')
    exit(1)
try:
    ckpt = torch.load(p, map_location='cpu')
    print('TYPE:', type(ckpt))
    if isinstance(ckpt, dict):
        print('KEYS:', list(ckpt.keys()))
        # print stored metadata
        print('STORED class_names:', ckpt.get('class_names'))
        print('STORED num_classes :', ckpt.get('num_classes'))
        # find model_state_dict
        msd = None
        for k in ['model_state_dict','state_dict','model']:
            if k in ckpt:
                msd = ckpt[k]
                print('FOUND', k)
                break
        if msd is None:
            msd = ckpt
        # inspect final layer params
        final_keys = [k for k in msd.keys() if k.startswith('fc') or 'classifier' in k]
        print('FINAL_KEYS_SAMPLE:', final_keys[:20])
        for k in final_keys:
            print(k, msd[k].shape)
    else:
        print('Checkpoint is a raw state_dict')
        print('KEYS SAMPLE:', list(ckpt.keys())[:20])
except Exception as e:
    print('ERR', e)
    import traceback; traceback.print_exc()
