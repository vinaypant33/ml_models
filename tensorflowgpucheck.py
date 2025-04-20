# # import tensorflow as tf, time

# # a = tf.random.normal([2000, 2000])
# # b = tf.random.normal([2000, 2000])

# # # CPU
# # with tf.device("/CPU:0"):
# #     t0 = time.time()
# #     tf.matmul(a, b).numpy()
# #     print("CPU time:", time.time() - t0)

# # # GPU (DirectML)
# # with tf.device("/GPU:0"):
# #     t0 = time.time()
# #     tf.matmul(a, b).numpy()
# #     print("GPU time:", time.time() - t0)



# import tensorflow as tf
# import time

# print("GPUs:", tf.config.list_physical_devices("GPU"))

# size = 10000  # increase this for more stress
# a = tf.random.normal([size, size])
# b = tf.random.normal([size, size])

# with tf.device("/GPU:0"):
#     print("Running heavy GPU matmul...")
#     start = time.time()
#     c = tf.matmul(a, b)
#     _ = c.numpy()
#     print("Time (s):", round(time.time() - start, 2))


import os, argparse, time, math, tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
p=argparse.ArgumentParser()
p.add_argument('--mode',type=str,default='gemm',choices=['gemm','cnn','memory'])
p.add_argument('--dtype',type=str,default='float16',choices=['float16','float32'])
p.add_argument('--prefill_gb',type=float,default=0.0)
p.add_argument('--chunks',type=int,default=32)
p.add_argument('--matrix',type=int,default=24000)
p.add_argument('--batch',type=int,default=1280)
p.add_argument('--steps',type=int,default=600)
p.add_argument('--warmup',type=int,default=10)
a=p.parse_args()
dtype={'float16':tf.float16,'float32':tf.float32}[a.dtype]
try:
    from tensorflow.keras import mixed_precision
    if a.dtype=='float16':
        mixed_precision.set_global_policy('mixed_float16')
except Exception:
    pass
g=tf.config.list_physical_devices('GPU')
if not g:
    print('No GPU detected'); exit(1)
L=tf.config.list_logical_devices('GPU')
print('GPUs:',g)
print('Logical:',L)
def gb2elems(gb,bytes_per):
    return int((gb*1024**3)//bytes_per)
def prefill(gb,chunks,dtype):
    if gb<=0: return []
    b=2 if dtype==tf.float16 else 4
    tot=gb2elems(gb,b)
    per=max(1,tot//chunks)
    side=int(math.sqrt(per))
    per=side*side
    bufs=[]
    with tf.device('/GPU:0'):
        for _ in range(chunks):
            bufs.append(tf.random.uniform([side,side],dtype=dtype))
    return bufs
def gemm(n,steps,warmup,dtype):
    with tf.device('/GPU:0'):
        a=tf.random.normal([n,n],dtype=dtype)
        b=tf.random.normal([n,n],dtype=dtype)
        for _ in range(warmup):
            c=tf.matmul(a,b); _=c.numpy()
        t=[]
        for i in range(steps):
            t0=time.time(); c=tf.matmul(a,b); _=c.numpy(); t1=time.time()
            t.append(t1-t0)
            if (i+1)%10==0: print('step',i+1,'avg_s',round(sum(t)/len(t),4))
        print('final_avg_s',round(sum(t)/len(t),4))
def ds(batch,steps,shape,dtype):
    def gen():
        while True:
            x=tf.random.normal([batch]+list(shape),dtype=dtype)
            y=tf.random.uniform([batch],maxval=1000,dtype=tf.int32)
            yield x,tf.one_hot(y,1000,dtype=tf.float32)
    d=tf.data.Dataset.from_generator(gen,output_signature=(tf.TensorSpec([batch]+list(shape),dtype),tf.TensorSpec([batch,1000],tf.float32)))
    return d.take(steps).prefetch(tf.data.AUTOTUNE)
def cnn(batch,steps,dtype):
    with tf.device('/GPU:0'):
        m=tf.keras.applications.ResNet50(weights=None,input_shape=(224,224,3),classes=1000)
        m.compile(optimizer=tf.keras.optimizers.Adam(1e-3),loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),metrics=['accuracy'])
        d=ds(batch,steps,(224,224,3),dtype)
        h=m.fit(d,epochs=1,steps_per_epoch=steps,verbose=1)
        print('loss',float(h.history['loss'][-1]),'acc',float(h.history['accuracy'][-1]))
def mem(bufs):
    s=0.0
    for t in bufs: s+=tf.reduce_sum(t).numpy()
    print('checksum',s)
with tf.device('/GPU:0'):
    bufs=prefill(a.prefill_gb,a.chunks,dtype)
if a.mode=='gemm':
    gemm(a.matrix,a.steps,a.warmup,dtype)
elif a.mode=='cnn':
    cnn(a.batch,a.steps,dtype)
elif a.mode=='memory':
    mem(bufs)
