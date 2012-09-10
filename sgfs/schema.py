import os

import yaml

from .structure import Structure
from . import utils




class Schema(object):
    
    def __init__(self, root, entity_type, config_name):
        
        self.root = root
        self.entity_type = entity_type
        self.config_name = config_name
        self.config = yaml.load(open(self._join_path(config_name)).read())
        
        # Set some defaults on the config.
        self.config.setdefault('type', 'entity')
        default_template = self._join_path(os.path.splitext(config_name)[0])
        if os.path.exists(default_template):
            self.config.setdefault('template', default_template)
        
        # Load all the children.
        self.children = {}
        for child_type, child_config_name in self.config.get('children', {}).iteritems():
            self.children[child_type] = Schema(root, child_type, child_config_name)
    
    def _join_path(self, *args):
        return os.path.join(self.root, *args)
    
    def __repr__(self):
        return '<Schema %s:%s at 0x%x>' % (os.path.basename(self.root), self.entity_type, id(self))
    
    def pprint(self, depth=0):
        print '%s%s "%s"' % (
            '\t' * depth,
            self.entity_type,
            self.config_name,
        ),
        if not self.children:
            print
            return
        
        print '{'
        for type_, child in sorted(self.children.iteritems()):
            child.pprint(depth + 1)
        print '\t' * depth + '}'
    
    def structure(self, context):
        
        # Make sure that this schema matches the context we have been asked to
        # create a structure for.
        if self.entity_type != context.entity['type']:
            raise ValueError('context entity type does not match; %r != %r' % (
                self.entity_type, context.entity['type']
            ))
        
        # Create the structure node for this entity.
        structure = Structure.from_context(context, self.config.copy())
        if not structure:
            return
        
        # Create all of the Context's child nodes as well.
        for child_context in context.children:
            child_type = child_context.entity['type']
            if child_type in self.children:
                child_structure = self.children[child_type].structure(child_context)
                if child_structure:
                    structure.children.append(child_structure)
        
        return structure
        
        


