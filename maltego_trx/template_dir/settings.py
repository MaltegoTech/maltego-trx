from maltego_trx.decorator_registry import TransformSetting

api_key_setting = TransformSetting(name='api_key',
                                   display_name='API Key',
                                   setting_type='string',
                                   global_setting=True)

language_setting = TransformSetting(name='language',
                                    display_name="Language",
                                    setting_type='string',
                                    default_value='en',
                                    optional=True,
                                    popup=True)
