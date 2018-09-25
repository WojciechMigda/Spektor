def pp_get_single_image(result=None, **kw):
    import base64
    result['image'] = base64.b64encode(result['image']).decode('utf8')
    result['thumb'] = base64.b64encode(result['thumb']).decode('utf8')
    pass

def pp_get_many_images(result=None, search_params=None, **kw):
    result['objects'] = [pp_get_single_image(d) or d for d in result['objects']]
    pass

def pp_post_image_in(data=None, **kw):
    import base64
    data['image'] = base64.b64decode(data['image'])
    data['thumb'] = base64.b64decode(data['thumb'])
    pass

def pp_post_image_out(result=None, **kw):
    import base64
    result['image'] = base64.b64encode(result['image']).decode('utf8')
    result['thumb'] = base64.b64encode(result['thumb']).decode('utf8')
    pass

postprocessors=dict(GET_SINGLE=[pp_get_single_image], GET_MANY=[pp_get_many_images], POST=[pp_post_image_out])
preprocessors=dict(POST=[pp_post_image_in])
