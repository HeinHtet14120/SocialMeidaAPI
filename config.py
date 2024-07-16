class Config:
    POOL_NAME = 'ws_pool'
    SECRET_KEY = 'c78b513e0a98931571350013c4e24fbc77496eee1563e8e2f30d93b5c2e46788'
    JWT_SECRET_KEY = 'c78b513e0a98931571350013c4e24fbc77496eee1563e8e2f30d93b5c2e46788'
    POST_IMAGES_FOLDER = 'post_images'
    USER_POST_IMAGES_FOLDER = 'user_images_folder'
    CATEGORY_IMAGES_FOLDER = 'category_images_folder'
    GROUP_IMAGES_FOLDER = 'category_groups'
    PROFILE_IMAGES_FOLDER = 'profile_image'
    QR_IMAGES_FOLDER = 'QR_Codes'
    NEWS_RELATED_FOLDER = 'news_related'
    EVENT_IMAGES_FOLDER = 'event_images'
    CLUB_IMAGES_FOLDER = 'club_images'
    

    TOKEN_EXPIRY_DATE = 30
    CONFIG_ORGANIZER_ROLE = 1
    IS_DEV = True  
    IS_TEST = False 

        # Development Server Configurations
    DATABASE_DEV = ''
    HOST_DEV = ''
    USERNAME_DEV = ''
    PASSWORD_DEV = ''
    SERVER_DOMAIN_DEV = 'http://127.0.0.1:5000/'

