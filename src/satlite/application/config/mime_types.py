def set_mime_types() -> None:
    from mimetypes import add_type

    add_type('text/javascript', '.js')
