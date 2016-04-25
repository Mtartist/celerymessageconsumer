import ConfigParser
import os


class LocalConfigParser(object):

    def __init__():
        pass

    @staticmethod
    def parse_configs(section=None):
        try:
            cur_dir = os.path.dirname(os.path.realpath(__file__))
            filename = os.path.join(cur_dir, 'configs.ini')
            print {"sender configs filename": filename}
            cparser = ConfigParser.ConfigParser()
            cparser.read(filename)
            config_dic = {}
            section = section or 'DB'
            options = cparser.options(section)
            for option in options:
                try:
                    config_dic[option] = cparser.get(section, option)
                    if config_dic[option] == -1:
                        print "Reading config Invalid section ", option, section
                except:
                    print {"Exception": option}
                    config_dic[option] = None
            return config_dic
        except Exception as e:
            print {"blunder opening configuration ": e}
            return {}

