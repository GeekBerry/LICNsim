def drawEdge(start, end, ax, width= 0.1, **kwargs):
    start= numpy.array(start)
    end= numpy.array(end)

    vec= end-start
    vec_len= numpy.linalg.norm(vec)

    n_vec= numpy.array([ vec[1], -vec[0] ]) # 左转90度
    n_vec= (n_vec/vec_len)* width # 线条偏移向量

    head_length= width*4
    head_width= width*2
    vec= vec* max(0, 1 - head_length/vec_len) # vec 缩短,使得 vec 加上 head_length 等于起终点距离

    ax.arrow( *(start+n_vec), *vec, width= width, head_width= head_width, head_length= head_length, shape= 'left', **kwargs)
