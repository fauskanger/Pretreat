from app.config import config


def resource(filename):
    path = '{0}/{1}'.format(config.strings.resource_path, filename)
    print("Resource path concat: {0}".format(path))
    return path


class PyThomas():

    @staticmethod
    def for_each_node_in(graph, lambda_method, is_reading_data=False):
        for node in graph.nodes(data=is_reading_data):
            if is_reading_data:
                node = node[0]
            lambda_method(node)


pythomas = PyThomas()