//
//  Item.swift
//  TruLedgr
//
//  Created by Nathan McGuire on 6/23/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
