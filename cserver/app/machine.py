class MachineManager(object):
    """
    @property _node_id
    This property will important to keep our node server work fine!
    Assume we have some situation like below.
    1, room server die, we try to connect it. after we reconnect success
    we don't want it rearrange our node id! so you will try to send a argument
    with the connect of http/websocket. so we have the below url!
    `ws://127.0.0.1:8888/ws?ip=127.0.0.1&port=9001&mode=1`
    mode = 1 is a example, maybe another! but for the first time, we send a `-1`
    as the argument! and that url will direct to `register`, and generate a node id!
    2, we run before room-server, the reconnect has try many time, but the `mode=-1`
    send to the room-server. so the room-server will understand we has not register!
    3, if the room-server die, it's hope to recovery by our data! so that's why we has this!
    """
    _node_id = -1

    """
    To keep the _node_id, only be changed one time!
    """
    _set_node_flag = True

    def set_node(self, node):
        """
        This is singleton pattern method! only first time has effective!
        so that can keep the node id work for all-life!
        Args:
            node:

        Returns:

        """
        if self._set_node_flag:
            self._node_id = node
            self._set_node_flag = False

    def help_recovery(self):
        """
        Send all data room-server need, so that can recovery data!
        Returns:

        """
        pass